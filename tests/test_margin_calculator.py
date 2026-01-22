"""
Tests for margin calculator service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.margin_calculator import MarginSettings, MarginCalculator
from app.models.cost_item import CostItem


class TestMarginSettings:
    """Tests for MarginSettings class."""
    
    def test_default_settings(self):
        """Test default margin settings."""
        settings = MarginSettings()
        assert settings.global_margin_percent == 20.0
        assert settings.group_margins == {}
    
    def test_calculate_selling_price_global(self):
        """Test selling price calculation with global margin."""
        settings = MarginSettings(global_margin_percent=25.0)
        purchase_price = 100.0
        
        selling_price = settings.calculate_selling_price(purchase_price)
        
        assert selling_price == 125.0
    
    def test_calculate_selling_price_group(self):
        """Test selling price calculation with group margin."""
        settings = MarginSettings(global_margin_percent=20.0)
        settings.set_group_margin("Materials", 30.0)
        
        purchase_price = 100.0
        
        # With group margin
        selling_price = settings.calculate_selling_price(purchase_price, group="Materials")
        assert selling_price == 130.0
        
        # Without group (uses global)
        selling_price = settings.calculate_selling_price(purchase_price, group="Other")
        assert selling_price == 120.0
    
    def test_calculate_selling_price_item_override(self):
        """Test selling price calculation with item-specific margin override."""
        settings = MarginSettings(global_margin_percent=20.0)
        settings.set_group_margin("Materials", 30.0)
        
        purchase_price = 100.0
        
        # Item override takes precedence
        selling_price = settings.calculate_selling_price(
            purchase_price, 
            group="Materials", 
            item_margin_override=15.0
        )
        assert selling_price == 115.0
    
    def test_calculate_purchase_price(self):
        """Test reverse calculation: selling price to purchase price."""
        settings = MarginSettings(global_margin_percent=25.0)
        selling_price = 125.0
        
        purchase_price = settings.calculate_purchase_price(selling_price)
        
        assert purchase_price == 100.0
    
    def test_get_margin_for_item(self):
        """Test getting applicable margin for an item."""
        settings = MarginSettings(global_margin_percent=20.0)
        settings.set_group_margin("Materials", 30.0)
        
        # Item override
        margin = settings.get_margin_for_item(item_margin_override=15.0)
        assert margin == 15.0
        
        # Group margin
        margin = settings.get_margin_for_item(group="Materials")
        assert margin == 30.0
        
        # Global margin
        margin = settings.get_margin_for_item(group="Other")
        assert margin == 20.0
    
    def test_set_remove_group_margin(self):
        """Test setting and removing group margins."""
        settings = MarginSettings()
        
        # Set margin
        settings.set_group_margin("Materials", 25.0)
        assert "Materials" in settings.group_margins
        assert settings.group_margins["Materials"] == 25.0
        
        # Remove margin
        settings.remove_group_margin("Materials")
        assert "Materials" not in settings.group_margins
    
    def test_to_dict_from_dict(self):
        """Test serialization and deserialization."""
        settings = MarginSettings(global_margin_percent=22.0)
        settings.set_group_margin("Materials", 28.0)
        settings.set_group_margin("Services", 35.0)
        
        # Serialize
        data = settings.to_dict()
        assert data['global_margin_percent'] == 22.0
        assert data['group_margins']['Materials'] == 28.0
        assert data['group_margins']['Services'] == 35.0
        
        # Deserialize
        restored = MarginSettings.from_dict(data)
        assert restored.global_margin_percent == 22.0
        assert restored.group_margins['Materials'] == 28.0
        assert restored.group_margins['Services'] == 35.0


class TestMarginCalculator:
    """Tests for MarginCalculator class."""
    
    def test_apply_margin_to_items_with_purchase_price(self):
        """Test applying margin to items with purchase prices."""
        settings = MarginSettings(global_margin_percent=20.0)
        calculator = MarginCalculator(settings)
        
        items = [
            CostItem(
                name="Item 1",
                quantity=1.0,
                unit="szt",
                price_unit_net=0.0,
                purchase_price=100.0
            ),
            CostItem(
                name="Item 2",
                quantity=2.0,
                unit="szt",
                price_unit_net=0.0,
                purchase_price=50.0
            )
        ]
        
        result = calculator.apply_margin_to_items(items)
        
        assert result[0].price_unit_net == 120.0
        assert result[1].price_unit_net == 60.0
    
    def test_apply_margin_to_items_without_purchase_price(self):
        """Test that items without purchase price keep their selling price."""
        settings = MarginSettings(global_margin_percent=20.0)
        calculator = MarginCalculator(settings)
        
        items = [
            CostItem(
                name="Item 1",
                quantity=1.0,
                unit="szt",
                price_unit_net=150.0,
                purchase_price=None
            )
        ]
        
        result = calculator.apply_margin_to_items(items)
        
        # Should remain unchanged
        assert result[0].price_unit_net == 150.0
    
    def test_apply_margin_with_group(self):
        """Test applying group-specific margins."""
        settings = MarginSettings(global_margin_percent=20.0)
        settings.set_group_margin("Materials", 30.0)
        calculator = MarginCalculator(settings)
        
        items = [
            CostItem(
                name="Material Item",
                quantity=1.0,
                unit="szt",
                price_unit_net=0.0,
                group="Materials",
                purchase_price=100.0
            ),
            CostItem(
                name="Other Item",
                quantity=1.0,
                unit="szt",
                price_unit_net=0.0,
                group="Services",
                purchase_price=100.0
            )
        ]
        
        result = calculator.apply_margin_to_items(items)
        
        assert result[0].price_unit_net == 130.0  # 30% margin
        assert result[1].price_unit_net == 120.0  # 20% global margin
    
    def test_apply_margin_with_item_override(self):
        """Test applying item-specific margin override."""
        settings = MarginSettings(global_margin_percent=20.0)
        calculator = MarginCalculator(settings)
        
        items = [
            CostItem(
                name="Custom Margin Item",
                quantity=1.0,
                unit="szt",
                price_unit_net=0.0,
                margin_percent=15.0,
                purchase_price=100.0
            )
        ]
        
        result = calculator.apply_margin_to_items(items)
        
        assert result[0].price_unit_net == 115.0  # 15% item-specific margin
    
    def test_get_margin_summary(self):
        """Test margin summary calculation."""
        settings = MarginSettings(global_margin_percent=20.0)
        calculator = MarginCalculator(settings)
        
        items = [
            CostItem(
                name="Item 1",
                quantity=2.0,
                unit="szt",
                price_unit_net=120.0,
                purchase_price=100.0
            ),
            CostItem(
                name="Item 2",
                quantity=1.0,
                unit="szt",
                price_unit_net=150.0,
                purchase_price=None  # No margin tracking
            )
        ]
        
        summary = calculator.get_margin_summary(items)
        
        assert summary['total_purchase_value'] == 200.0  # 2 * 100
        assert summary['total_selling_value'] == 240.0   # 2 * 120
        assert summary['total_margin_value'] == 40.0     # 240 - 200
        assert summary['overall_margin_percent'] == 20.0
        assert summary['items_with_margin'] == 1
        assert summary['total_items'] == 2
    
    def test_get_margin_summary_no_margin_items(self):
        """Test margin summary with no margin-tracked items."""
        settings = MarginSettings()
        calculator = MarginCalculator(settings)
        
        items = [
            CostItem(
                name="Item 1",
                quantity=1.0,
                unit="szt",
                price_unit_net=100.0,
                purchase_price=None
            )
        ]
        
        summary = calculator.get_margin_summary(items)
        
        assert summary['total_purchase_value'] == 0.0
        assert summary['total_selling_value'] == 0.0
        assert summary['total_margin_value'] == 0.0
        assert summary['overall_margin_percent'] == 0.0
        assert summary['items_with_margin'] == 0
        assert summary['total_items'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
