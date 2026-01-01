"""
Models for flashing (obróbki blacharskie) profiles and materials.
"""

from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class FlashingProfile:
    """
    Represents a flashing profile with dimensions and pricing.
    """
    id: str
    name: str
    description: str
    development_width: float  # Rozwinięcie w mm
    material_type: str  # stal, aluminium, miedź
    price_per_meter: float
    unit_conversions: Dict[str, float]  # {"m2_per_meter": 0.3, "kg_per_meter": 1.2}
    is_custom: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FlashingProfile':
        """Create FlashingProfile from dictionary."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            development_width=float(data.get('development_width', 0.0)),
            material_type=data.get('material_type', 'stal'),
            price_per_meter=float(data.get('price_per_meter', 0.0)),
            unit_conversions=data.get('unit_conversions', {}),
            is_custom=bool(data.get('is_custom', False))
        )
    
    def calculate_sheet_length(self, width_mm: float) -> float:
        """
        Calculate required sheet length for given width.
        
        Args:
            width_mm: Width in millimeters
            
        Returns:
            Required length in meters
        """
        # Convert to meters and account for development width
        return (width_mm / 1000.0) * (self.development_width / 1000.0)
    
    def calculate_area(self, length_m: float) -> float:
        """
        Calculate area from length.
        
        Args:
            length_m: Length in meters
            
        Returns:
            Area in square meters
        """
        conversion = self.unit_conversions.get('m2_per_meter', self.development_width / 1000.0)
        return length_m * conversion
    
    def calculate_weight(self, length_m: float) -> float:
        """
        Calculate weight from length.
        
        Args:
            length_m: Length in meters
            
        Returns:
            Weight in kilograms
        """
        conversion = self.unit_conversions.get('kg_per_meter', 0.0)
        return length_m * conversion


@dataclass
class FlashingMaterial:
    """
    Represents a material used for flashings.
    """
    id: str
    name: str
    material_type: str  # stal, aluminium, miedź
    thickness_mm: float
    coating: str  # powłoka (np. polyester, mat, miedź natur)
    price_per_m2: float
    price_per_kg: Optional[float] = None
    weight_per_m2: Optional[float] = None  # kg/m²
    color: str = ""
    supplier: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FlashingMaterial':
        """Create FlashingMaterial from dictionary."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            material_type=data.get('material_type', 'stal'),
            thickness_mm=float(data.get('thickness_mm', 0.0)),
            coating=data.get('coating', ''),
            price_per_m2=float(data.get('price_per_m2', 0.0)),
            price_per_kg=float(data['price_per_kg']) if data.get('price_per_kg') else None,
            weight_per_m2=float(data['weight_per_m2']) if data.get('weight_per_m2') else None,
            color=data.get('color', ''),
            supplier=data.get('supplier', '')
        )
    
    def calculate_price_by_area(self, area_m2: float) -> float:
        """Calculate price by area."""
        return area_m2 * self.price_per_m2
    
    def calculate_price_by_weight(self, weight_kg: float) -> float:
        """Calculate price by weight."""
        if self.price_per_kg:
            return weight_kg * self.price_per_kg
        return 0.0
