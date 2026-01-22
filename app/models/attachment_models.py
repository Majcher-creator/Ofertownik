"""
Attachment models for cost estimates.
Supports images, PDFs, and drawings.
"""

from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class Attachment:
    """
    Represents an attachment (file) associated with a cost estimate or item.
    """
    id: str
    filename: str
    original_path: str
    stored_path: str
    file_type: str  # 'image', 'pdf', 'drawing', 'other'
    size_bytes: int
    created_at: datetime
    description: str = ""
    thumbnail_path: str = ""
    linked_item_id: Optional[str] = None  # Link to specific cost item, or None for estimate-level
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Attachment':
        """Create Attachment from dictionary."""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        return cls(
            id=data.get('id', ''),
            filename=data.get('filename', ''),
            original_path=data.get('original_path', ''),
            stored_path=data.get('stored_path', ''),
            file_type=data.get('file_type', 'other'),
            size_bytes=int(data.get('size_bytes', 0)),
            created_at=created_at,
            description=data.get('description', ''),
            thumbnail_path=data.get('thumbnail_path', ''),
            linked_item_id=data.get('linked_item_id')
        )
    
    @staticmethod
    def detect_file_type(filename: str) -> str:
        """
        Detect file type from filename extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            File type string
        """
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            return 'image'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in ['.dwg', '.dxf', '.svg']:
            return 'drawing'
        else:
            return 'other'
    
    def get_display_size(self) -> str:
        """Get human-readable file size."""
        size = self.size_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
