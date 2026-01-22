"""
Margin calculator service for cost estimate items.
Calculates selling prices based on purchase prices and margin percentages.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class MarginSettings:
    """
    Settings for margin calculations.
    Supports global margin, per-group margins, and per-item overrides.
    """
    global_margin_percent: float = 20.0
    group_margins: Dict[str, float] = field(default_factory=dict)
    
    def calculate_selling_price(self, purchase_price: float, 
                               group: Optional[str] = None,
                               item_margin_override: Optional[float] = None) -> float:
        """
        Calculate selling price from purchase price using applicable margin.
        
        Priority order:
        1. Item-specific margin override
        2. Group margin (if item belongs to a group)
        3. Global margin
        
        Args:
            purchase_price: The purchase/cost price
            group: Group name (if item belongs to a group)
            item_margin_override: Item-specific margin override (if any)
            
        Returns:
            Calculated selling price
        """
        # Determine which margin to use
        if item_margin_override is not None:
            margin = item_margin_override
        elif group and group in self.group_margins:
            margin = self.group_margins[group]
        else:
            margin = self.global_margin_percent
        
        # Calculate selling price
        return round(purchase_price * (1 + margin / 100.0), 2)
    
    def calculate_purchase_price(self, selling_price: float,
                                group: Optional[str] = None,
                                item_margin_override: Optional[float] = None) -> float:
        """
        Calculate purchase price from selling price using applicable margin.
        
        This is the reverse calculation of calculate_selling_price.
        
        Args:
            selling_price: The selling price
            group: Group name (if item belongs to a group)
            item_margin_override: Item-specific margin override (if any)
            
        Returns:
            Calculated purchase price
        """
        # Determine which margin to use
        if item_margin_override is not None:
            margin = item_margin_override
        elif group and group in self.group_margins:
            margin = self.group_margins[group]
        else:
            margin = self.global_margin_percent
        
        # Calculate purchase price
        return round(selling_price / (1 + margin / 100.0), 2)
    
    def get_margin_for_item(self, group: Optional[str] = None,
                           item_margin_override: Optional[float] = None) -> float:
        """
        Get the applicable margin percentage for an item.
        
        Args:
            group: Group name (if item belongs to a group)
            item_margin_override: Item-specific margin override (if any)
            
        Returns:
            Applicable margin percentage
        """
        if item_margin_override is not None:
            return item_margin_override
        elif group and group in self.group_margins:
            return self.group_margins[group]
        else:
            return self.global_margin_percent
    
    def set_group_margin(self, group: str, margin_percent: float) -> None:
        """
        Set margin percentage for a specific group.
        
        Args:
            group: Group name
            margin_percent: Margin percentage for the group
        """
        self.group_margins[group] = margin_percent
    
    def remove_group_margin(self, group: str) -> None:
        """
        Remove group-specific margin, falling back to global margin.
        
        Args:
            group: Group name
        """
        if group in self.group_margins:
            del self.group_margins[group]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'global_margin_percent': self.global_margin_percent,
            'group_margins': self.group_margins
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MarginSettings':
        """Create from dictionary."""
        return cls(
            global_margin_percent=float(data.get('global_margin_percent', 20.0)),
            group_margins=data.get('group_margins', {})
        )


class MarginCalculator:
    """
    Calculator for managing margins in cost estimates.
    """
    
    def __init__(self, settings: Optional[MarginSettings] = None):
        """
        Initialize the margin calculator.
        
        Args:
            settings: MarginSettings instance, or None to use defaults
        """
        self.settings = settings or MarginSettings()
    
    def apply_margin_to_items(self, items: list) -> list:
        """
        Apply margin calculations to a list of cost items.
        
        Updates price_unit_net based on purchase_price and applicable margin.
        If purchase_price is not set, price_unit_net is treated as the final price.
        
        Args:
            items: List of CostItem objects
            
        Returns:
            Updated list of items
        """
        for item in items:
            if item.purchase_price is not None:
                # Calculate selling price from purchase price
                item.price_unit_net = self.settings.calculate_selling_price(
                    item.purchase_price,
                    group=item.group if hasattr(item, 'group') else None,
                    item_margin_override=item.margin_percent if hasattr(item, 'margin_percent') else None
                )
            # If purchase_price is None, price_unit_net is already the selling price
            
            # Recalculate totals
            if hasattr(item, 'calculate_totals'):
                item.calculate_totals()
        
        return items
    
    def get_margin_summary(self, items: list) -> Dict:
        """
        Get summary of margins applied to items.
        
        Args:
            items: List of CostItem objects
            
        Returns:
            Dictionary with margin statistics
        """
        total_purchase = 0.0
        total_selling = 0.0
        items_with_margin = 0
        
        for item in items:
            if hasattr(item, 'purchase_price') and item.purchase_price is not None:
                items_with_margin += 1
                total_purchase += item.purchase_price * item.quantity
                total_selling += item.price_unit_net * item.quantity
        
        overall_margin_percent = 0.0
        if total_purchase > 0:
            overall_margin_percent = ((total_selling - total_purchase) / total_purchase) * 100
        
        return {
            'total_purchase_value': round(total_purchase, 2),
            'total_selling_value': round(total_selling, 2),
            'total_margin_value': round(total_selling - total_purchase, 2),
            'overall_margin_percent': round(overall_margin_percent, 2),
            'items_with_margin': items_with_margin,
            'total_items': len(items)
        }
