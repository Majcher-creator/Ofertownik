"""
Version models for cost estimate history and version control.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Version:
    """
    Represents a single version of a cost estimate.
    """
    id: str
    version_number: int
    created_at: datetime
    author: str
    description: str
    snapshot: Dict[str, Any]  # Complete state of the estimate at this version
    changes: List[str] = field(default_factory=list)  # List of changes from previous version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary representation."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Version':
        """Create Version instance from dictionary."""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        return cls(
            id=data.get('id', ''),
            version_number=int(data.get('version_number', 1)),
            created_at=created_at,
            author=data.get('author', 'Unknown'),
            description=data.get('description', ''),
            snapshot=data.get('snapshot', {}),
            changes=data.get('changes', [])
        )


@dataclass
class VersionHistory:
    """
    Represents the complete version history of a cost estimate.
    """
    estimate_id: str
    versions: List[Version] = field(default_factory=list)
    
    def add_version(self, version: Version) -> None:
        """Add a new version to the history."""
        self.versions.append(version)
        # Sort by version number
        self.versions.sort(key=lambda v: v.version_number)
    
    def get_version(self, version_number: int) -> Optional[Version]:
        """Get a specific version by number."""
        for version in self.versions:
            if version.version_number == version_number:
                return version
        return None
    
    def get_latest_version(self) -> Optional[Version]:
        """Get the most recent version."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)
    
    def get_next_version_number(self) -> int:
        """Get the next version number."""
        if not self.versions:
            return 1
        return max(v.version_number for v in self.versions) + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'estimate_id': self.estimate_id,
            'versions': [v.to_dict() for v in self.versions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionHistory':
        """Create VersionHistory instance from dictionary."""
        history = cls(estimate_id=data.get('estimate_id', ''))
        for version_data in data.get('versions', []):
            version = Version.from_dict(version_data)
            history.add_version(version)
        return history
