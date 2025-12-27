"""
Cost item model for the Ofertownik application.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CostItem:
    """
    Represents a single item in a cost estimate.
    """
    name: str
    quantity: float
    unit: str
    price_unit_net: float
    vat_rate: int = 23
    category: str = "material"  # "material" or "service"
    note: str = ""
    
    # Calculated fields (computed by cost_calculations)
    total_net: float = 0.0
    vat_value: float = 0.0
    total_gross: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cost item to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CostItem':
        """Create CostItem instance from dictionary."""
        return cls(
            name=data.get('name', ''),
            quantity=float(data.get('quantity', 0.0)),
            unit=data.get('unit', ''),
            price_unit_net=float(data.get('price_unit_net', 0.0)),
            vat_rate=int(data.get('vat_rate', 23)),
            category=data.get('category', 'material'),
            note=data.get('note', ''),
            total_net=float(data.get('total_net', 0.0)),
            vat_value=float(data.get('vat_value', 0.0)),
            total_gross=float(data.get('total_gross', 0.0))
        )
    
    def calculate_totals(self) -> None:
        """Calculate total net, VAT value, and total gross for this item."""
        self.total_net = round(self.quantity * self.price_unit_net, 2)
        self.vat_value = round(self.total_net * self.vat_rate / 100.0, 2)
        self.total_gross = round(self.total_net + self.vat_value, 2)
