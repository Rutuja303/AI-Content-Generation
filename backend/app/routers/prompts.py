from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Prompt, GeneratedPost
from app.schemas import PromptCreate, Prompt as PromptSchema, ContentGenerationRequest, ContentGenerationResponse
from app.core.auth import get_current_active_user
from app.services.ai_service import AIService
from app.services.file_service import file_service

router = APIRouter()
ai_service = AIService()

@router.post("/", response_model=PromptSchema)
def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_prompt = Prompt(
        user_id=current_user.id,
        prompt_text=prompt_data.prompt_text
    )
    
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    
    return db_prompt

@router.get("/", response_model=List[PromptSchema])
def get_prompts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    prompts = db.query(Prompt).filter(
        Prompt.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return prompts

@router.get("/{prompt_id}", response_model=PromptSchema)
def get_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    return prompt

@router.delete("/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    db.delete(prompt)
    db.commit()
    
    return {"message": "Prompt deleted successfully"}

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    import json
    
    # Check content type
    content_type = request.headers.get("content-type", "")
    print(f"DEBUG: Content-Type: {content_type}")
    
    if "multipart/form-data" in content_type:
        # Handle FormData (with files)
        form_data = await request.form()
        prompt = form_data.get("prompt")
        platforms_str = form_data.get("platforms")
        files = form_data.getlist("files")
        
        print(f"DEBUG: FormData - prompt: {prompt}")
        print(f"DEBUG: FormData - platforms: {platforms_str}")
        print(f"DEBUG: FormData - files: {files}")
        
    elif "application/json" in content_type:
        # Handle JSON (legacy support)
        body = await request.json()
        prompt = body.get("prompt")
        platforms_list = body.get("platforms", [])
        files = []
        
        print(f"DEBUG: JSON - prompt: {prompt}")
        print(f"DEBUG: JSON - platforms: {platforms_list}")
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type"
        )
    
    # Parse platforms if it's a string
    if isinstance(platforms_str, str):
        try:
            platforms_list = json.loads(platforms_str)
            print(f"DEBUG: Parsed platforms: {platforms_list}")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid platforms format"
            )
    
    # Save uploaded files if any
    media_files = []
    if files and len(files) > 0:
        # Convert to UploadFile objects if needed
        upload_files = []
        for file in files:
            if hasattr(file, 'filename'):  # Already an UploadFile
                upload_files.append(file)
            else:  # Convert to UploadFile
                from fastapi import UploadFile
                upload_files.append(UploadFile(file=file, filename=getattr(file, 'name', 'unknown')))
        
        media_files = await file_service.save_uploaded_files(upload_files)
    
    # Create prompt
    db_prompt = Prompt(
        user_id=current_user.id,
        prompt_text=prompt
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    
    # Generate content for each platform with media analysis
    generated_content = await ai_service.generate_platform_content(
        prompt, platforms_list, media_files
    )
    
    # Save generated posts
    generated_posts = []
    for platform, content in generated_content.items():
        db_post = GeneratedPost(
            user_id=current_user.id,
            prompt_id=db_prompt.id,
            platform=platform,
            content=content,
            status="draft"
        )
        db.add(db_post)
        generated_posts.append(db_post)
    
    db.commit()
    
    # Refresh posts to get IDs
    for post in generated_posts:
        db.refresh(post)
    
    return ContentGenerationResponse(
        prompt_id=db_prompt.id,
        generated_posts=generated_posts
    )

@router.post("/{prompt_id}/regenerate")
def regenerate_content(
    prompt_id: int,
    platforms: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get existing prompt
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Generate new content
    generated_content = ai_service.generate_platform_content(
        prompt.prompt_text, platforms
    )
    
    # Update or create posts
    for platform, content in generated_content.items():
        existing_post = db.query(GeneratedPost).filter(
            GeneratedPost.prompt_id == prompt_id,
            GeneratedPost.platform == platform
        ).first()
        
        if existing_post:
            existing_post.content = content
            existing_post.status = "draft"
        else:
            new_post = GeneratedPost(
                user_id=current_user.id,
                prompt_id=prompt_id,
                platform=platform,
                content=content,
                status="draft"
            )
            db.add(new_post)
    
    db.commit()
    
    return {"message": "Content regenerated successfully"}
