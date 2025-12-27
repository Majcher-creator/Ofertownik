"""
Client data model for the Ofertownik application.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Client:
    """
    Represents a client in the roofing cost estimator system.
    """
    name: str
    address: str = ""
    id: str = ""  # NIP or other tax ID
    phone: str = ""
    email: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert client to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        """Create Client instance from dictionary."""
        return cls(
            name=data.get('name', ''),
            address=data.get('address', ''),
            id=data.get('id', ''),
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
    
    def is_valid(self) -> bool:
        """Check if client has minimum required data."""
        return bool(self.name and self.name.strip())
