from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from app.database import engine, Base
from app.routers import auth, prompts, posts, schedule, publish, analytics, oauth, content
from app.routers import settings as settings_router
from app.core.config import settings
from app.core.auth import get_current_user

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Content Generator API...")
    yield
    # Shutdown
    print("Shutting down Content Generator API...")

app = FastAPI(
    title="AI Content Generator API",
    description="API for generating and managing multi-platform social media content",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(schedule.router, prefix="/schedule", tags=["Scheduling"])
app.include_router(publish.router, prefix="/publish", tags=["Publishing"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
app.include_router(content.router, prefix="/content", tags=["Content Management"])
app.include_router(settings_router.router, tags=["Settings"])

@app.get("/")
async def root():
    return {
        "message": "AI Content Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
