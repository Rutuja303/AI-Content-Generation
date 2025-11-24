from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_active_user
from app.models import User, GeneratedPost, PlatformConnection
from app.schemas import GeneratedPostCreate, GeneratedPostResponse
from typing import List
from datetime import datetime
import httpx
import json

router = APIRouter(tags=["content"])

@router.post("/drafts", response_model=GeneratedPostResponse)
async def create_draft(
    post_data: GeneratedPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new draft post"""
    try:
        # Create the draft post
        draft = GeneratedPost(
            user_id=current_user.id,
            platform=post_data.platform,
            content=post_data.content,
            status="draft"
        )
        
        db.add(draft)
        db.commit()
        db.refresh(draft)
        
        return GeneratedPostResponse(
            id=draft.id,
            platform=draft.platform,
            content=draft.content,
            status=draft.status,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create draft: {str(e)}")

@router.get("/drafts", response_model=List[GeneratedPostResponse])
async def get_drafts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all draft posts for the current user"""
    try:
        drafts = db.query(GeneratedPost).filter(
            GeneratedPost.user_id == current_user.id,
            GeneratedPost.status == "draft"
        ).order_by(GeneratedPost.created_at.desc()).all()
        
        return [
            GeneratedPostResponse(
                id=draft.id,
                platform=draft.platform,
                content=draft.content,
                status=draft.status,
                created_at=draft.created_at,
                updated_at=draft.updated_at
            )
            for draft in drafts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch drafts: {str(e)}")

@router.put("/drafts/{draft_id}", response_model=GeneratedPostResponse)
async def update_draft(
    draft_id: int,
    post_data: GeneratedPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing draft post"""
    try:
        draft = db.query(GeneratedPost).filter(
            GeneratedPost.id == draft_id,
            GeneratedPost.user_id == current_user.id,
            GeneratedPost.status == "draft"
        ).first()
        
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        draft.content = post_data.content
        draft.platform = post_data.platform
        draft.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(draft)
        
        return GeneratedPostResponse(
            id=draft.id,
            platform=draft.platform,
            content=draft.content,
            status=draft.status,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update draft: {str(e)}")

@router.delete("/drafts/{draft_id}")
async def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a draft post"""
    try:
        draft = db.query(GeneratedPost).filter(
            GeneratedPost.id == draft_id,
            GeneratedPost.user_id == current_user.id,
            GeneratedPost.status == "draft"
        ).first()
        
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        db.delete(draft)
        db.commit()
        
        return {"message": "Draft deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete draft: {str(e)}")

@router.post("/drafts/{draft_id}/post")
async def post_to_social_media(
    draft_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Post a draft to the connected social media platform"""
    try:
        # Get the draft
        draft = db.query(GeneratedPost).filter(
            GeneratedPost.id == draft_id,
            GeneratedPost.user_id == current_user.id,
            GeneratedPost.status == "draft"
        ).first()
        
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        # Get the platform connection
        connection = db.query(PlatformConnection).filter(
            PlatformConnection.user_id == current_user.id,
            PlatformConnection.platform == draft.platform,
            PlatformConnection.is_active == True
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=400, 
                detail=f"No active connection found for {draft.platform}. Please connect your {draft.platform} account first."
            )
        
        # Post to the social media platform
        success = await post_to_platform(draft.platform, draft.content, connection)
        
        if success:
            # Update draft status to published
            draft.status = "published"
            draft.updated_at = datetime.utcnow()
            db.commit()
            
            return {"message": f"Successfully posted to {draft.platform}!", "status": "published"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to post to {draft.platform}")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in post_to_social_media: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to post: {str(e)}")

async def post_to_platform(platform: str, content: str, connection: PlatformConnection) -> bool:
    """Post content to the specified social media platform"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {connection.access_token}"}
            
            if platform == "linkedin":
                # LinkedIn API endpoint for posting
                url = "https://api.linkedin.com/v2/ugcPosts"
                
                # If platform_user_id is unknown, try to get it from the token
                author_urn = connection.platform_user_id
                if author_urn == "unknown":
                    # Try to get user info from the access token
                    try:
                        user_info_url = "https://api.linkedin.com/v2/me?projection=(id,localizedFirstName,localizedLastName)"
                        user_response = await client.get(user_info_url, headers=headers)
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            author_urn = user_data.get("id", "unknown")
                            print(f"Retrieved LinkedIn user ID: {author_urn}")
                        else:
                            print(f"Failed to get LinkedIn user info: {user_response.status_code} - {user_response.text}")
                            return False
                    except Exception as e:
                        print(f"Error getting LinkedIn user info: {e}")
                        return False
                
                post_data = {
                    "author": f"urn:li:person:{author_urn}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
                
                response = await client.post(url, json=post_data, headers=headers)
                print(f"LinkedIn post response: {response.status_code} - {response.text}")
                return response.status_code == 201
                
            elif platform == "twitter":
                # Twitter API endpoint for posting
                url = "https://api.twitter.com/2/tweets"
                post_data = {"text": content}
                
                response = await client.post(url, json=post_data, headers=headers)
                print(f"Twitter post response: {response.status_code} - {response.text}")
                return response.status_code == 201
                
            elif platform == "facebook":
                # Facebook API endpoint for posting
                url = f"https://graph.facebook.com/v18.0/{connection.platform_user_id}/feed"
                post_data = {"message": content}
                
                response = await client.post(url, data=post_data, headers=headers)
                print(f"Facebook post response: {response.status_code} - {response.text}")
                return response.status_code == 200
                
            elif platform == "instagram":
                # Instagram API endpoint for posting
                url = f"https://graph.facebook.com/v18.0/{connection.platform_user_id}/media"
                post_data = {
                    "image_url": "https://via.placeholder.com/1080x1080",  # Placeholder image
                    "caption": content
                }
                
                response = await client.post(url, data=post_data, headers=headers)
                print(f"Instagram post response: {response.status_code} - {response.text}")
                return response.status_code == 200
                
            else:
                print(f"Unsupported platform: {platform}")
                return False
                
    except Exception as e:
        print(f"Error posting to {platform}: {str(e)}")
        return False
