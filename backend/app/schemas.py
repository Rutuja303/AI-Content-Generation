from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Prompt schemas
class PromptBase(BaseModel):
    prompt_text: str

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Generated Post schemas
class GeneratedPostBase(BaseModel):
    platform: str
    content: str
    status: str

class GeneratedPostCreate(GeneratedPostBase):
    prompt_id: int

class GeneratedPost(GeneratedPostBase):
    id: int
    prompt_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Scheduled Post schemas
class ScheduledPostBase(BaseModel):
    platform: str
    scheduled_time: datetime

class ScheduledPostCreate(ScheduledPostBase):
    generated_post_id: int

class ScheduledPost(ScheduledPostBase):
    id: int
    generated_post_id: int
    status: str
    published_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Platform Connection schemas
class PlatformConnectionBase(BaseModel):
    platform: str
    platform_username: Optional[str]

class PlatformConnectionCreate(PlatformConnectionBase):
    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[datetime]

class PlatformConnectionResponse(BaseModel):
    id: int
    user_id: int
    platform: str
    platform_username: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PlatformConnection(PlatformConnectionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class GeneratedPostCreate(BaseModel):
    platform: str
    content: str

class GeneratedPostResponse(BaseModel):
    id: int
    platform: str
    content: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Content Generation schemas
class ContentGenerationRequest(BaseModel):
    prompt: str
    platforms: List[str]  # ["twitter", "instagram", "linkedin", "facebook", "email"]

class ContentGenerationResponse(BaseModel):
    prompt_id: int
    generated_posts: List[GeneratedPost]

# Publishing schemas
class PublishRequest(BaseModel):
    generated_post_id: int
    platform: str
    schedule_time: Optional[datetime] = None

class PublishResponse(BaseModel):
    success: bool
    message: str
    scheduled_post_id: Optional[int] = None

# Analytics schemas
class AnalyticsResponse(BaseModel):
    total_posts: int
    published_posts: int
    scheduled_posts: int
    platform_breakdown: dict
    recent_activity: List[dict]

# Password change schema
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
