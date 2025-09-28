"""
File upload utilities for handling media files.
Supports multiple cloud storage providers.
"""

import os
import uuid
import mimetypes
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import aiofiles
from pathlib import Path


class FileUploadError(Exception):
    """Custom exception for file upload errors."""
    pass


class FileUploader:
    """Base file uploader class."""
    
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.allowed_types = settings.ALLOWED_FILE_TYPES
    
    async def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        # Check file size
        if file.size and file.size > self.max_file_size:
            raise FileUploadError(
                f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Check file type
        if file.content_type not in self.allowed_types:
            raise FileUploadError(
                f"File type {file.content_type} not allowed. Allowed types: {self.allowed_types}"
            )
        
        # Check file extension
        if file.filename:
            ext = Path(file.filename).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.mp4']:
                raise FileUploadError("Invalid file extension")
    
    async def generate_filename(self, original_filename: str, user_id: str) -> str:
        """Generate unique filename."""
        ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{user_id}_{unique_id}{ext}"
    
    async def save_file_locally(self, file: UploadFile, filename: str) -> str:
        """Save file to local storage (for development)."""
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Return URL path
        return f"/uploads/{filename}"
    
    async def upload_to_cloud(self, file: UploadFile, filename: str) -> str:
        """Upload file to cloud storage (AWS S3, Cloudinary, etc.)."""
        # TODO: Implement cloud storage upload
        # For now, fallback to local storage
        return await self.save_file_locally(file, filename)
    
    async def create_thumbnail(self, file_path: str, filename: str) -> Optional[str]:
        """Create thumbnail for image files."""
        # TODO: Implement thumbnail creation using PIL/Pillow
        # For now, return None
        return None


class LocalFileUploader(FileUploader):
    """Local file uploader for development."""
    
    async def upload_file(
        self, 
        file: UploadFile, 
        user_id: str
    ) -> Tuple[str, Optional[str]]:
        """Upload file and return (file_url, thumbnail_url)."""
        await self.validate_file(file)
        
        filename = await self.generate_filename(file.filename, user_id)
        
        # Reset file pointer
        await file.seek(0)
        
        # Upload file
        file_url = await self.save_file_locally(file, filename)
        
        # Create thumbnail if it's an image
        thumbnail_url = None
        if file.content_type and file.content_type.startswith('image/'):
            thumbnail_url = await self.create_thumbnail(file_url, filename)
        
        return file_url, thumbnail_url


class CloudFileUploader(FileUploader):
    """Cloud file uploader for production."""
    
    async def upload_file(
        self, 
        file: UploadFile, 
        user_id: str
    ) -> Tuple[str, Optional[str]]:
        """Upload file to cloud storage."""
        await self.validate_file(file)
        
        filename = await self.generate_filename(file.filename, user_id)
        
        # Reset file pointer
        await file.seek(0)
        
        # Upload to cloud
        file_url = await self.upload_to_cloud(file, filename)
        
        # Create thumbnail if it's an image
        thumbnail_url = None
        if file.content_type and file.content_type.startswith('image/'):
            thumbnail_url = await self.create_thumbnail(file_url, filename)
        
        return file_url, thumbnail_url


# Factory function to get appropriate uploader
def get_file_uploader() -> FileUploader:
    """Get file uploader based on environment."""
    if settings.DEBUG:
        return LocalFileUploader()
    else:
        return CloudFileUploader()


# Convenience function for API endpoints
async def upload_media_file(
    file: UploadFile, 
    user_id: str
) -> Tuple[str, Optional[str]]:
    """
    Upload media file and return URLs.
    
    Args:
        file: Uploaded file
        user_id: User ID for file organization
    
    Returns:
        Tuple of (file_url, thumbnail_url)
    
    Raises:
        HTTPException: If file validation fails
    """
    try:
        uploader = get_file_uploader()
        file_url, thumbnail_url = await uploader.upload_file(file, user_id)
        return file_url, thumbnail_url
    except FileUploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
