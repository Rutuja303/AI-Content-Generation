from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, GeneratedPost, Prompt
from app.schemas import GeneratedPost as GeneratedPostSchema
from app.core.auth import get_current_active_user
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.get("/", response_model=List[GeneratedPostSchema])
def get_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    platform: str = None,
    status: str = None
):
    query = db.query(GeneratedPost).join(Prompt).filter(Prompt.user_id == current_user.id)
    
    if platform:
        query = query.filter(GeneratedPost.platform == platform)
    
    if status:
        query = query.filter(GeneratedPost.status == status)
    
    posts = query.offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=GeneratedPostSchema)
def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post

@router.put("/{post_id}", response_model=GeneratedPostSchema)
def update_post(
    post_id: int,
    content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post.content = content
    post.status = "draft"
    db.commit()
    db.refresh(post)
    
    return post

@router.patch("/{post_id}/approve")
def approve_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post.status = "approved"
    db.commit()
    
    return {"message": "Post approved successfully"}

@router.patch("/{post_id}/reject")
def reject_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post.status = "rejected"
    db.commit()
    
    return {"message": "Post rejected successfully"}

@router.post("/{post_id}/improve")
def improve_post(
    post_id: int,
    feedback: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Use AI to improve the content based on feedback
    improved_content = ai_service.improve_content(
        post.content, post.platform, feedback
    )
    
    post.content = improved_content
    post.status = "draft"
    db.commit()
    db.refresh(post)
    
    return {"message": "Post improved successfully", "content": improved_content}

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}
