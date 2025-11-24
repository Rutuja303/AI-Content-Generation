from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import User, ScheduledPost, GeneratedPost, Prompt
from app.schemas import ScheduledPostCreate, ScheduledPost as ScheduledPostSchema
from app.core.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ScheduledPostSchema)
def schedule_post(
    schedule_data: ScheduledPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify the generated post belongs to the user
    generated_post = db.query(GeneratedPost).join(Prompt).filter(
        GeneratedPost.id == schedule_data.generated_post_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not generated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated post not found"
        )
    
    # Check if post is already scheduled
    existing_schedule = db.query(ScheduledPost).filter(
        ScheduledPost.generated_post_id == schedule_data.generated_post_id,
        ScheduledPost.platform == schedule_data.platform
    ).first()
    
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already scheduled for this platform"
        )
    
    # Create scheduled post
    scheduled_post = ScheduledPost(
        generated_post_id=schedule_data.generated_post_id,
        platform=schedule_data.platform,
        scheduled_time=schedule_data.scheduled_time,
        status="scheduled"
    )
    
    db.add(scheduled_post)
    db.commit()
    db.refresh(scheduled_post)
    
    return scheduled_post

@router.get("/", response_model=List[ScheduledPostSchema])
def get_scheduled_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None
):
    query = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id
    )
    
    if status:
        query = query.filter(ScheduledPost.status == status)
    
    scheduled_posts = query.offset(skip).limit(limit).all()
    return scheduled_posts

@router.get("/{schedule_id}", response_model=ScheduledPostSchema)
def get_scheduled_post(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    scheduled_post = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        ScheduledPost.id == schedule_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    return scheduled_post

@router.put("/{schedule_id}", response_model=ScheduledPostSchema)
def update_scheduled_post(
    schedule_id: int,
    scheduled_time: datetime,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    scheduled_post = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        ScheduledPost.id == schedule_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    if scheduled_post.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update published or failed posts"
        )
    
    scheduled_post.scheduled_time = scheduled_time
    db.commit()
    db.refresh(scheduled_post)
    
    return scheduled_post

@router.delete("/{schedule_id}")
def cancel_scheduled_post(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    scheduled_post = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        ScheduledPost.id == schedule_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    if scheduled_post.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel published or failed posts"
        )
    
    db.delete(scheduled_post)
    db.commit()
    
    return {"message": "Scheduled post cancelled successfully"}

@router.get("/upcoming", response_model=List[ScheduledPostSchema])
def get_upcoming_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    upcoming_posts = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        ScheduledPost.status == "scheduled",
        ScheduledPost.scheduled_time > datetime.utcnow()
    ).order_by(ScheduledPost.scheduled_time).limit(limit).all()
    
    return upcoming_posts
