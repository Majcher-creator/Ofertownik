"""
Data models for gutter systems and accessories.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class GutterAccessory:
    """
    Represents a single accessory in a gutter system.
    """
    name: str
    unit: str
    price_unit_net: float
    quantity: float = 0.0
    vat_rate: int = 8
    category: str = "material"
    auto_calculate: bool = True  # Whether quantity is auto-calculated
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GutterAccessory':
        """Create GutterAccessory from dictionary."""
        return cls(
            name=data.get('name', ''),
            unit=data.get('unit', ''),
            price_unit_net=float(data.get('price_unit_net', 0.0)),
            quantity=float(data.get('quantity', 0.0)),
            vat_rate=int(data.get('vat_rate', 8)),
            category=data.get('category', 'material'),
            auto_calculate=data.get('auto_calculate', True)
        )


@dataclass
class GutterSystem:
    """
    Represents a complete gutter system with all its accessories and prices.
    """
    name: str
    system_type: str  # "pvc", "steel", "copper", "zinc-titanium"
    description: str = ""
    accessories: List[GutterAccessory] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'system_type': self.system_type,
            'description': self.description,
            'accessories': [acc.to_dict() for acc in self.accessories]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GutterSystem':
        """Create GutterSystem from dictionary."""
        accessories_data = data.get('accessories', [])
        accessories = [GutterAccessory.from_dict(acc) for acc in accessories_data]
        
        return cls(
            name=data.get('name', ''),
            system_type=data.get('system_type', ''),
            description=data.get('description', ''),
            accessories=accessories
        )
    
    def get_accessory(self, name: str) -> Optional[GutterAccessory]:
        """Get accessory by name."""
        for acc in self.accessories:
            if acc.name == name:
                return acc
        return None
    
    def update_accessory_quantity(self, name: str, quantity: float) -> bool:
        """Update quantity for a specific accessory."""
        acc = self.get_accessory(name)
        if acc:
            acc.quantity = quantity
            return True
        return False


@dataclass
class GutterTemplate:
    """
    Represents a saved template configuration for a gutter system.
    Can be predefined or user-created.
    """
    name: str
    system: GutterSystem
    is_predefined: bool = False
    created_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'system': self.system.to_dict(),
            'is_predefined': self.is_predefined,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GutterTemplate':
        """Create GutterTemplate from dictionary."""
        system = GutterSystem.from_dict(data.get('system', {}))
        
        return cls(
            name=data.get('name', ''),
            system=system,
            is_predefined=data.get('is_predefined', False),
            created_at=data.get('created_at', '')
        )
