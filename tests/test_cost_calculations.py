"""
Unit tests for cost calculation functions.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_calculations import compute_item, compute_totals


class TestCostCalculations:
    """Test suite for cost calculation functions."""
    
    def test_compute_item_basic(self):
        """Test basic item computation."""
        item = {
            "name": "Papa wierzchnia",
            "quantity": 10.0,
            "unit": "m2",
            "price_unit_net": 35.0,
            "vat_rate": 23,
            "category": "material"
        }
        
        result = compute_item(item)
        
        assert result['total_net'] == 350.0
        assert result['vat_value'] == 80.5  # 350 * 0.23
        assert result['total_gross'] == 430.5
    
    def test_compute_item_zero_vat(self):
        """Test item computation with 0% VAT."""
        item = {
            "name": "Test item",
            "quantity": 5.0,
            "price_unit_net": 20.0,
            "vat_rate": 0
        }
        
        result = compute_item(item)
        
        assert result['total_net'] == 100.0
        assert result['vat_value'] == 0.0
        assert result['total_gross'] == 100.0
    
    def test_compute_item_vat_8(self):
        """Test item computation with 8% VAT."""
        item = {
            "name": "Test item",
            "quantity": 10.0,
            "price_unit_net": 100.0,
            "vat_rate": 8
        }
        
        result = compute_item(item)
        
        assert result['total_net'] == 1000.0
        assert result['vat_value'] == 80.0
        assert result['total_gross'] == 1080.0
    
    def test_compute_totals_simple(self):
        """Test totals computation with simple items."""
        items = [
            {
                "name": "Item 1",
                "quantity": 10.0,
                "unit": "m2",
                "price_unit_net": 10.0,
                "vat_rate": 23,
                "category": "material"
            },
            {
                "name": "Item 2",
                "quantity": 5.0,
                "unit": "szt",
                "price_unit_net": 20.0,
                "vat_rate": 23,
                "category": "service"
            }
        ]
        
        result = compute_totals(items, transport_percent=0.0, transport_vat=23)
        
        # Item 1: 10 * 10 = 100, VAT = 23, gross = 123
        # Item 2: 5 * 20 = 100, VAT = 23, gross = 123
        # Total: net = 200, vat = 46, gross = 246
        
        assert result['summary']['net'] == 200.0
        assert result['summary']['vat'] == 46.0
        assert result['summary']['gross'] == 246.0
    
    def test_compute_totals_with_transport(self):
        """Test totals computation with transport."""
        items = [
            {
                "name": "Item 1",
                "quantity": 10.0,
                "unit": "m2",
                "price_unit_net": 10.0,
                "vat_rate": 23,
                "category": "material"
            }
        ]
        
        result = compute_totals(items, transport_percent=3.0, transport_vat=23)
        
        # Item net: 100
        # Transport: 3% of 100 = 3
        # Transport VAT: 3 * 0.23 = 0.69
        # Total net: 100 + 3 = 103
        # Total VAT: 23 + 0.69 = 23.69
        # Total gross: 103 + 23.69 = 126.69
        
        assert result['transport']['net'] == 3.0
        assert result['transport']['percent'] == 3.0
        assert result['summary']['net'] == 103.0
        assert abs(result['summary']['vat'] - 23.69) < 0.01
        assert abs(result['summary']['gross'] - 126.69) < 0.01
    
    def test_compute_totals_by_vat(self):
        """Test grouping by VAT rate."""
        items = [
            {
                "name": "Item 23%",
                "quantity": 10.0,
                "price_unit_net": 10.0,
                "vat_rate": 23,
                "category": "material"
            },
            {
                "name": "Item 8%",
                "quantity": 10.0,
                "price_unit_net": 10.0,
                "vat_rate": 8,
                "category": "material"
            }
        ]
        
        result = compute_totals(items, transport_percent=0.0, transport_vat=23)
        
        assert 23 in result['by_vat']
        assert 8 in result['by_vat']
        assert result['by_vat'][23]['net'] == 100.0
        assert result['by_vat'][8]['net'] == 100.0
    
    def test_compute_totals_by_category(self):
        """Test grouping by category."""
        items = [
            {
                "name": "Material",
                "quantity": 10.0,
                "price_unit_net": 10.0,
                "vat_rate": 23,
                "category": "material"
            },
            {
                "name": "Service",
                "quantity": 5.0,
                "price_unit_net": 20.0,
                "vat_rate": 23,
                "category": "service"
            }
        ]
        
        result = compute_totals(items, transport_percent=0.0, transport_vat=23)
        
        assert 'material' in result['by_category']
        assert 'service' in result['by_category']
        assert result['by_category']['material']['net'] == 100.0
        assert result['by_category']['service']['net'] == 100.0
    
    def test_compute_totals_empty_items(self):
        """Test with empty items list."""
        result = compute_totals([], transport_percent=0.0, transport_vat=23)
        
        assert result['summary']['net'] == 0.0
        assert result['summary']['vat'] == 0.0
        assert result['summary']['gross'] == 0.0
    
    def test_rounding_precision(self):
        """Test that values are properly rounded to 2 decimal places."""
        item = {
            "name": "Test",
            "quantity": 3.333,
            "price_unit_net": 1.111,
            "vat_rate": 23
        }
        
        result = compute_item(item)
        
        # Check that all values have at most 2 decimal places
        assert len(str(result['total_net']).split('.')[-1]) <= 2
        assert len(str(result['vat_value']).split('.')[-1]) <= 2
        assert len(str(result['total_gross']).split('.')[-1]) <= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
