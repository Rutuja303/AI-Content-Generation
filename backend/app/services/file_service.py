import os
import shutil
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path
import uuid
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different file types
        self.images_dir = self.upload_dir / "images"
        self.videos_dir = self.upload_dir / "videos"
        self.images_dir.mkdir(exist_ok=True)
        self.videos_dir.mkdir(exist_ok=True)
        
        # Supported file types
        self.supported_image_types = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        self.supported_video_types = {".mp4", ".avi", ".mov", ".webm", ".mkv"}
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    async def save_uploaded_files(self, files: List[UploadFile]) -> List[str]:
        """
        Save uploaded files and return their paths
        """
        saved_files = []
        
        for file in files:
            try:
                # Validate file
                if not self._validate_file(file):
                    continue
                
                # Generate unique filename
                file_ext = Path(file.filename).suffix.lower()
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                
                # Determine save directory
                if file_ext in self.supported_image_types:
                    save_dir = self.images_dir
                elif file_ext in self.supported_video_types:
                    save_dir = self.videos_dir
                else:
                    continue
                
                # Save file
                file_path = save_dir / unique_filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                saved_files.append(str(file_path))
                logger.info(f"Saved file: {file_path}")
                
            except Exception as e:
                logger.error(f"Error saving file {file.filename}: {str(e)}")
                continue
        
        return saved_files
    
    def _validate_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded file
        """
        # Check file size
        if hasattr(file, 'size') and file.size and file.size > self.max_file_size:
            logger.warning(f"File {file.filename} too large: {file.size} bytes")
            return False
        
        # Check file extension
        if not file.filename:
            return False
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.supported_image_types and file_ext not in self.supported_video_types:
            logger.warning(f"Unsupported file type: {file_ext}")
            return False
        
        return True
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the filesystem
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            file_path_obj = Path(file_path)
            file_ext = file_path_obj.suffix.lower()
            
            return {
                "filename": file_path_obj.name,
                "extension": file_ext,
                "size": os.path.getsize(file_path),
                "type": "image" if file_ext in self.supported_image_types else "video",
                "path": file_path
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up files older than specified hours
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for directory in [self.images_dir, self.videos_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            logger.info(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error cleaning up file {file_path}: {str(e)}")

# Global instance
file_service = FileService()
