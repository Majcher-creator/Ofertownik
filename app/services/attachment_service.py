"""
Service for managing attachments in cost estimates.
"""

import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime

from app.models.attachment_models import Attachment

# Optional PIL for thumbnail generation
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class AttachmentManager:
    """
    Manages attachments for cost estimates.
    Handles file copying, thumbnail generation, and organization.
    """
    
    def __init__(self, attachments_dir: str = "attachments"):
        """
        Initialize the attachment manager.
        
        Args:
            attachments_dir: Directory for storing attachments
        """
        self.attachments_dir = attachments_dir
        self.thumbnails_dir = os.path.join(attachments_dir, "thumbnails")
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        os.makedirs(self.attachments_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
    
    def add_attachment(self, file_path: str, description: str = "",
                      linked_item_id: Optional[str] = None) -> Optional[Attachment]:
        """
        Add a new attachment.
        
        Args:
            file_path: Path to the file to attach
            description: Optional description
            linked_item_id: Optional link to a specific cost item
            
        Returns:
            Created Attachment or None if failed
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        try:
            # Generate unique ID and filename
            attachment_id = str(uuid.uuid4())
            original_filename = os.path.basename(file_path)
            _, ext = os.path.splitext(original_filename)
            stored_filename = f"{attachment_id}{ext}"
            stored_path = os.path.join(self.attachments_dir, stored_filename)
            
            # Copy file
            shutil.copy2(file_path, stored_path)
            
            # Get file info
            size_bytes = os.path.getsize(stored_path)
            file_type = Attachment.detect_file_type(original_filename)
            
            # Generate thumbnail for images
            thumbnail_path = ""
            if file_type == 'image' and PIL_AVAILABLE:
                thumbnail_path = self._generate_thumbnail(stored_path, attachment_id)
            
            # Create attachment object
            attachment = Attachment(
                id=attachment_id,
                filename=original_filename,
                original_path=file_path,
                stored_path=stored_path,
                file_type=file_type,
                size_bytes=size_bytes,
                created_at=datetime.now(),
                description=description,
                thumbnail_path=thumbnail_path,
                linked_item_id=linked_item_id
            )
            
            return attachment
            
        except Exception as e:
            print(f"Error adding attachment: {e}")
            return None
    
    def remove_attachment(self, attachment: Attachment) -> bool:
        """
        Remove an attachment and its associated files.
        
        Args:
            attachment: Attachment to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove main file
            if os.path.exists(attachment.stored_path):
                os.remove(attachment.stored_path)
            
            # Remove thumbnail
            if attachment.thumbnail_path and os.path.exists(attachment.thumbnail_path):
                os.remove(attachment.thumbnail_path)
            
            return True
            
        except Exception as e:
            print(f"Error removing attachment: {e}")
            return False
    
    def _generate_thumbnail(self, image_path: str, attachment_id: str,
                          size: tuple = (200, 200)) -> str:
        """
        Generate thumbnail for an image.
        
        Args:
            image_path: Path to the image
            attachment_id: Attachment ID
            size: Thumbnail size (width, height)
            
        Returns:
            Path to generated thumbnail, or empty string if failed
        """
        if not PIL_AVAILABLE:
            return ""
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Generate thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_filename = f"thumb_{attachment_id}.jpg"
                thumbnail_path = os.path.join(self.thumbnails_dir, thumbnail_filename)
                img.save(thumbnail_path, 'JPEG', quality=85)
                
                return thumbnail_path
                
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return ""
    
    def get_attachments_for_estimate(self, attachments: List[Attachment]) -> List[Attachment]:
        """
        Filter attachments that are associated with the estimate (not linked to specific items).
        
        Args:
            attachments: List of all attachments
            
        Returns:
            List of estimate-level attachments
        """
        return [a for a in attachments if a.linked_item_id is None]
    
    def get_attachments_for_item(self, attachments: List[Attachment], 
                                item_id: str) -> List[Attachment]:
        """
        Get attachments linked to a specific item.
        
        Args:
            attachments: List of all attachments
            item_id: Item ID
            
        Returns:
            List of attachments for the item
        """
        return [a for a in attachments if a.linked_item_id == item_id]
    
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage information
        """
        total_size = 0
        file_count = 0
        
        if os.path.exists(self.attachments_dir):
            for filename in os.listdir(self.attachments_dir):
                file_path = os.path.join(self.attachments_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        return {
            'total_size_bytes': total_size,
            'file_count': file_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
