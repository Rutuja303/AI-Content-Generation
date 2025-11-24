from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, GeneratedPost, ScheduledPost, Prompt
from app.schemas import AnalyticsResponse
from app.core.auth import get_current_active_user

router = APIRouter()

@router.get("/dashboard", response_model=AnalyticsResponse)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get total posts
    total_posts = db.query(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id
    ).count()
    
    # Get published posts
    published_posts = db.query(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        GeneratedPost.status == "published"
    ).count()
    
    # Get scheduled posts
    scheduled_posts = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        ScheduledPost.status == "scheduled"
    ).count()
    
    # Platform breakdown
    platform_breakdown = db.query(
        GeneratedPost.platform,
        func.count(GeneratedPost.id).label('count')
    ).join(Prompt).filter(
        Prompt.user_id == current_user.id
    ).group_by(GeneratedPost.platform).all()
    
    platform_stats = {platform: count for platform, count in platform_breakdown}
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_posts = db.query(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        GeneratedPost.created_at >= week_ago
    ).order_by(GeneratedPost.created_at.desc()).limit(10).all()
    
    recent_activity = [
        {
            "id": post.id,
            "platform": post.platform,
            "status": post.status,
            "created_at": post.created_at,
            "content_preview": post.content[:100] + "..." if len(post.content) > 100 else post.content
        }
        for post in recent_posts
    ]
    
    return AnalyticsResponse(
        total_posts=total_posts,
        published_posts=published_posts,
        scheduled_posts=scheduled_posts,
        platform_breakdown=platform_stats,
        recent_activity=recent_activity
    )

@router.get("/platform-stats")
def get_platform_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Posts by platform and status
    platform_stats = db.query(
        GeneratedPost.platform,
        GeneratedPost.status,
        func.count(GeneratedPost.id).label('count')
    ).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        GeneratedPost.created_at >= start_date
    ).group_by(GeneratedPost.platform, GeneratedPost.status).all()
    
    # Organize data
    stats = {}
    for platform, status, count in platform_stats:
        if platform not in stats:
            stats[platform] = {}
        stats[platform][status] = count
    
    return stats

@router.get("/timeline")
def get_content_timeline(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = 7
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get posts created in the specified time period
    posts = db.query(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        GeneratedPost.created_at >= start_date
    ).order_by(GeneratedPost.created_at.desc()).all()
    
    # Group by date
    timeline = {}
    for post in posts:
        date_key = post.created_at.strftime("%Y-%m-%d")
        if date_key not in timeline:
            timeline[date_key] = []
        
        timeline[date_key].append({
            "id": post.id,
            "platform": post.platform,
            "status": post.status,
            "content_preview": post.content[:50] + "..." if len(post.content) > 50 else post.content
        })
    
    return timeline

@router.get("/performance")
def get_performance_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # This would typically integrate with social media APIs to get actual metrics
    # For now, we'll provide placeholder data
    
    # Get posts by status
    status_counts = db.query(
        GeneratedPost.status,
        func.count(GeneratedPost.id).label('count')
    ).join(Prompt).filter(
        Prompt.user_id == current_user.id
    ).group_by(GeneratedPost.status).all()
    
    status_metrics = {status: count for status, count in status_counts}
    
    # Placeholder engagement metrics (would come from social media APIs)
    engagement_metrics = {
        "total_impressions": 0,
        "total_engagement": 0,
        "average_engagement_rate": 0.0,
        "top_performing_platform": "twitter",
        "best_posting_time": "10:00 AM"
    }
    
    return {
        "status_metrics": status_metrics,
        "engagement_metrics": engagement_metrics
    }

@router.get("/scheduled-overview")
def get_scheduled_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get upcoming scheduled posts
    upcoming_posts = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        ScheduledPost.status == "scheduled",
        ScheduledPost.scheduled_time > datetime.utcnow()
    ).order_by(ScheduledPost.scheduled_time).limit(10).all()
    
    # Get failed posts
    failed_posts = db.query(ScheduledPost).join(GeneratedPost).join(Prompt).filter(
        Prompt.user_id == current_user.id,
        ScheduledPost.status == "failed"
    ).order_by(ScheduledPost.created_at.desc()).limit(5).all()
    
    return {
        "upcoming_posts": [
            {
                "id": post.id,
                "platform": post.platform,
                "scheduled_time": post.scheduled_time,
                "content_preview": post.generated_post.content[:50] + "..." if len(post.generated_post.content) > 50 else post.generated_post.content
            }
            for post in upcoming_posts
        ],
        "failed_posts": [
            {
                "id": post.id,
                "platform": post.platform,
                "error_message": post.error_message,
                "scheduled_time": post.scheduled_time
            }
            for post in failed_posts
        ]
    }
