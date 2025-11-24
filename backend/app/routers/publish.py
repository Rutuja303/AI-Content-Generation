from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import User, GeneratedPost, Prompt, PlatformConnection, ScheduledPost
from app.schemas import PublishRequest, PublishResponse
from app.core.auth import get_current_active_user
from app.services.social_media_service import SocialMediaManager

router = APIRouter()
social_media_manager = SocialMediaManager()

@router.post("/", response_model=PublishResponse)
def publish_post(
    request: PublishRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get the generated post
    generated_post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == request.generated_post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not generated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated post not found"
        )
    
    # Get platform connection
    platform_connection = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == request.platform,
        PlatformConnection.is_active == True
    ).first()
    
    if not platform_connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active connection found for {request.platform}"
        )
    
    # If scheduling is requested
    if request.schedule_time:
        scheduled_post = ScheduledPost(
            generated_post_id=request.generated_post_id,
            platform=request.platform,
            scheduled_time=request.schedule_time,
            status="scheduled"
        )
        
        db.add(scheduled_post)
        db.commit()
        db.refresh(scheduled_post)
        
        return PublishResponse(
            success=True,
            message="Post scheduled successfully",
            scheduled_post_id=scheduled_post.id
        )
    
    # Publish immediately
    try:
        result = social_media_manager.publish_content(
            platform=request.platform,
            content=generated_post.content,
            access_token=platform_connection.access_token,
            access_token_secret=getattr(platform_connection, 'access_token_secret', None)
        )
        
        if result["success"]:
            # Update post status
            generated_post.status = "published"
            db.commit()
            
            return PublishResponse(
                success=True,
                message=result["message"]
            )
        else:
            return PublishResponse(
                success=False,
                message=f"Failed to publish: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        return PublishResponse(
            success=False,
            message=f"Publishing failed: {str(e)}"
        )

@router.get("/connections", response_model=List[dict])
def get_platform_connections(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    connections = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.is_active == True
    ).all()
    
    return [
        {
            "id": conn.id,
            "platform": conn.platform,
            "platform_username": conn.platform_username,
            "created_at": conn.created_at
        }
        for conn in connections
    ]

@router.post("/connections")
def add_platform_connection(
    platform: str,
    access_token: str,
    platform_username: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if connection already exists
    existing_connection = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == platform,
        PlatformConnection.is_active == True
    ).first()
    
    if existing_connection:
        # Update existing connection
        existing_connection.access_token = access_token
        existing_connection.platform_username = platform_username
        existing_connection.updated_at = datetime.utcnow()
    else:
        # Create new connection
        new_connection = PlatformConnection(
            user_id=current_user.id,
            platform=platform,
            access_token=access_token,
            platform_username=platform_username
        )
        db.add(new_connection)
    
    db.commit()
    
    return {"message": f"{platform} connection added successfully"}

@router.delete("/connections/{connection_id}")
def remove_platform_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.id == connection_id,
        PlatformConnection.user_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform connection not found"
        )
    
    connection.is_active = False
    db.commit()
    
    return {"message": "Platform connection removed successfully"}

@router.post("/test-connection")
def test_platform_connection(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == platform,
        PlatformConnection.is_active == True
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform connection not found"
        )
    
    try:
        # Test the connection with a simple API call
        result = social_media_manager.publish_content(
            platform=platform,
            content="Test connection - this is a test post",
            access_token=connection.access_token,
            access_token_secret=getattr(connection, 'access_token_secret', None)
        )
        
        return {
            "success": result["success"],
            "message": result.get("message", result.get("error", "Unknown result"))
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}"
        }
