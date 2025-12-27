"""
Material data model for the Ofertownik application.
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Material:
    """
    Represents a material or service in the database.
    """
    name: str
    unit: str = ""
    price_net: float = 0.0
    vat_rate: int = 23
    category: str = "material"  # "material" or "service"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert material to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Material':
        """Create Material instance from dictionary."""
        return cls(
            name=data.get('name', ''),
            unit=data.get('unit', ''),
            price_net=float(data.get('price_net', 0.0)),
            vat_rate=int(data.get('vat_rate', 23)),
            category=data.get('category', 'material'),
            description=data.get('description', '')
        )
