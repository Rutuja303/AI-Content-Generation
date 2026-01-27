from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/content_generator"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # AI Models
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Google Gemini (Free tier: 15 requests/minute)
    GEMINI_API_KEY: str = ""
    
    # Groq (Free tier: 14,400 requests/day)
    GROQ_API_KEY: str = ""
    
    # OAuth - Twitter
    TWITTER_CLIENT_ID: str = ""
    TWITTER_CLIENT_SECRET: str = ""
    
    # Twitter API (for posting content)
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    
    # Twitter Access Tokens (optional - for direct posting without OAuth)
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    
    # OAuth - LinkedIn
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    
    # OAuth - Facebook
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    
    # OAuth - Instagram
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    
    
    class Config:
        env_file = "../.env"  # Look for .env in project root
        case_sensitive = True
        extra = "allow"  # Allow extra environment variables

settings = Settings()
