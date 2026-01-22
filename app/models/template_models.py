"""
Template models for cost estimates.
Allows saving and loading cost estimate templates.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class CostEstimateTemplate:
    """
    Represents a saved template for a cost estimate.
    Templates can be reused to quickly create similar estimates.
    """
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    items: List[Dict[str, Any]] = field(default_factory=list)  # List of cost items as dicts
    groups: List[str] = field(default_factory=list)  # List of group names
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CostEstimateTemplate':
        """
        Create template instance from dictionary.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            CostEstimateTemplate instance
        """
        # Parse datetime fields
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.now()
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            created_at=created_at,
            updated_at=updated_at,
            items=data.get('items', []),
            groups=data.get('groups', []),
            metadata=data.get('metadata', {})
        )
