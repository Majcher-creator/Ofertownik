"""
Unit tests for validation utilities.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.validation import (
    validate_cost_item,
    validate_client,
    validate_nip,
    validate_positive_number,
    validate_dimensions
)


class TestValidation:
    """Test suite for validation functions."""
    
    def test_validate_cost_item_valid(self):
        """Test validation of valid cost item."""
        item = {
            'name': 'Test Item',
            'quantity': 10.0,
            'price_unit_net': 25.50,
            'vat_rate': 23
        }
        
        is_valid, msg = validate_cost_item(item)
        assert is_valid
        assert msg == ""
    
    def test_validate_cost_item_no_name(self):
        """Test validation fails with no name."""
        item = {
            'name': '',
            'quantity': 10.0,
            'price_unit_net': 25.50
        }
        
        is_valid, msg = validate_cost_item(item)
        assert not is_valid
        assert "Nazwa" in msg
    
    def test_validate_cost_item_negative_quantity(self):
        """Test validation fails with negative quantity."""
        item = {
            'name': 'Test',
            'quantity': -5.0,
            'price_unit_net': 25.50
        }
        
        is_valid, msg = validate_cost_item(item)
        assert not is_valid
        assert "Ilość" in msg
    
    def test_validate_cost_item_negative_price(self):
        """Test validation fails with negative price."""
        item = {
            'name': 'Test',
            'quantity': 10.0,
            'price_unit_net': -25.50
        }
        
        is_valid, msg = validate_cost_item(item)
        assert not is_valid
        assert "Cena" in msg
    
    def test_validate_cost_item_invalid_vat(self):
        """Test validation fails with invalid VAT rate."""
        item = {
            'name': 'Test',
            'quantity': 10.0,
            'price_unit_net': 25.50,
            'vat_rate': 15  # Invalid, should be 0, 8, or 23
        }
        
        is_valid, msg = validate_cost_item(item)
        assert not is_valid
        assert "VAT" in msg
    
    def test_validate_client_valid(self):
        """Test validation of valid client."""
        client = {
            'name': 'Test Client',
            'address': 'Test Street 123',
            'email': 'test@example.com'
        }
        
        is_valid, msg = validate_client(client)
        assert is_valid
        assert msg == ""
    
    def test_validate_client_no_name(self):
        """Test validation fails with no name."""
        client = {
            'name': '',
            'address': 'Test Street'
        }
        
        is_valid, msg = validate_client(client)
        assert not is_valid
        assert "Nazwa" in msg or "klienta" in msg
    
    def test_validate_client_invalid_email(self):
        """Test validation fails with invalid email."""
        client = {
            'name': 'Test Client',
            'email': 'invalid-email'
        }
        
        is_valid, msg = validate_client(client)
        assert not is_valid
        assert "e-mail" in msg.lower()
    
    def test_validate_nip_valid(self):
        """Test validation of valid NIP numbers."""
        # Valid NIP: 5260250274
        assert validate_nip("5260250274")
        assert validate_nip("526-025-02-74")
        assert validate_nip("526 025 02 74")
    
    def test_validate_nip_invalid_length(self):
        """Test validation fails with wrong length."""
        assert not validate_nip("123")
        assert not validate_nip("12345678901")
    
    def test_validate_nip_invalid_checksum(self):
        """Test validation fails with invalid checksum."""
        assert not validate_nip("1234567890")
    
    def test_validate_nip_non_numeric(self):
        """Test validation fails with non-numeric characters."""
        assert not validate_nip("abcd567890")
    
    def test_validate_positive_number_valid(self):
        """Test validation of positive numbers."""
        is_valid, msg = validate_positive_number(10.5)
        assert is_valid
        assert msg == ""
        
        is_valid, msg = validate_positive_number(0)
        assert is_valid
    
    def test_validate_positive_number_negative(self):
        """Test validation fails with negative number."""
        is_valid, msg = validate_positive_number(-5.0)
        assert not is_valid
        assert "ujemna" in msg.lower()
    
    def test_validate_positive_number_invalid_type(self):
        """Test validation fails with invalid type."""
        is_valid, msg = validate_positive_number("not a number")
        assert not is_valid
        assert "liczbą" in msg.lower()
    
    def test_validate_dimensions_valid(self):
        """Test validation of valid dimensions."""
        is_valid, msg = validate_dimensions(10.0, 8.0)
        assert is_valid
        assert msg == ""
    
    def test_validate_dimensions_negative(self):
        """Test validation fails with negative dimensions."""
        is_valid, msg = validate_dimensions(-10.0, 8.0)
        assert not is_valid
        
        is_valid, msg = validate_dimensions(10.0, -8.0)
        assert not is_valid
    
    def test_validate_dimensions_zero(self):
        """Test validation fails with zero dimensions."""
        is_valid, msg = validate_dimensions(0.0, 8.0)
        assert not is_valid
        assert "zero" in msg.lower()
        
        is_valid, msg = validate_dimensions(10.0, 0.0)
        assert not is_valid
    
    def test_validate_dimensions_invalid_type(self):
        """Test validation fails with invalid types."""
        is_valid, msg = validate_dimensions("ten", 8.0)
        assert not is_valid
        
        is_valid, msg = validate_dimensions(10.0, "eight")
        assert not is_valid


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
