from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.models import User, UserSettings
from app.core.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter()

class SettingsUpdate(BaseModel):
    notifications: Dict[str, Any] = {}
    privacy: Dict[str, Any] = {}

@router.get("/settings")
def get_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not user_settings:
        # Return default settings
        return {
            "notifications": {
                "email_notifications": True,
                "push_notifications": True,
                "content_approvals": True,
                "scheduled_posts": True,
                "analytics_reports": False,
                "security_alerts": True
            },
            "privacy": {
                "profile_visibility": "public",
                "content_visibility": "public",
                "analytics_sharing": False,
                "data_collection": True
            }
        }
    
    # Parse settings JSON
    settings = user_settings.settings or {}
    return {
        "notifications": settings.get("notifications", {
            "email_notifications": True,
            "push_notifications": True,
            "content_approvals": True,
            "scheduled_posts": True,
            "analytics_reports": False,
            "security_alerts": True
        }),
        "privacy": settings.get("privacy", {
            "profile_visibility": "public",
            "content_visibility": "public",
            "analytics_sharing": False,
            "data_collection": True
        })
    }

@router.put("/settings")
def update_user_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not user_settings:
        # Create new settings record
        user_settings = UserSettings(
            user_id=current_user.id,
            settings={
                "notifications": settings_data.notifications,
                "privacy": settings_data.privacy
            }
        )
        db.add(user_settings)
    else:
        # Update existing settings
        current_settings = user_settings.settings or {}
        current_settings.update({
            "notifications": settings_data.notifications,
            "privacy": settings_data.privacy
        })
        user_settings.settings = current_settings
    
    db.commit()
    db.refresh(user_settings)
    
    return {
        "message": "Settings saved successfully",
        "settings": {
            "notifications": settings_data.notifications,
            "privacy": settings_data.privacy
        }
    }

