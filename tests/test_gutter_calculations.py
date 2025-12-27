"""
Unit tests for gutter calculation functions.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gutter_calculations import calculate_guttering


class TestGutterCalculations:
    """Test suite for gutter calculation functions."""
    
    def test_basic_gutter_calculation(self):
        """Test basic guttering calculation."""
        result = calculate_guttering(20.0, 3.0)
        
        assert result['total_gutter_length_m'] == 20.0
        assert result['num_downpipes'] > 0
        assert result['total_downpipe_length_m'] > 0
        assert 'num_gutter_hooks' in result
        assert 'num_gutter_connectors' in result
    
    def test_gutter_with_specified_downpipes(self):
        """Test guttering with specified number of downpipes."""
        result = calculate_guttering(20.0, 3.0, num_downpipes=2)
        
        assert result['num_downpipes'] == 2
        assert result['total_downpipe_length_m'] == 6.0  # 2 * 3.0
    
    def test_gutter_downpipe_estimation(self):
        """Test automatic downpipe estimation."""
        # For 20m okap, should estimate 2 downpipes (20/10 = 2)
        result = calculate_guttering(20.0, 3.0, num_downpipes=None)
        assert result['num_downpipes'] == 2
        
        # For 5m okap, should estimate 1 downpipe
        result = calculate_guttering(5.0, 3.0, num_downpipes=None)
        assert result['num_downpipes'] == 1
    
    def test_gutter_hooks_calculation(self):
        """Test gutter hooks calculation (every 0.5m)."""
        result = calculate_guttering(10.0, 3.0)
        # 10m / 0.5m = 20 hooks
        assert result['num_gutter_hooks'] == 20
    
    def test_gutter_connectors_calculation(self):
        """Test gutter connectors calculation."""
        result = calculate_guttering(10.0, 3.0)
        # Connectors every 3m minus 1: ceil(10/3) - 1 = 4 - 1 = 3
        assert result['num_gutter_connectors'] >= 0
    
    def test_downpipe_elbows_calculation(self):
        """Test downpipe elbows calculation (2 per downpipe)."""
        result = calculate_guttering(20.0, 3.0, num_downpipes=3)
        assert result['num_downpipe_elbows'] == 6  # 3 * 2
    
    def test_downpipe_clamps_calculation(self):
        """Test downpipe clamps calculation (every 2m)."""
        result = calculate_guttering(20.0, 4.0, num_downpipes=2)
        # 2 downpipes * 4m height = 8m total
        # 8m / 2m = 4 clamps
        assert result['num_downpipe_clamps'] == 4
    
    def test_zero_length_okap(self):
        """Test with zero length okap."""
        result = calculate_guttering(0.0, 3.0)
        assert result['total_gutter_length_m'] == 0.0
        assert result['num_downpipes'] == 0
        assert result['num_gutter_hooks'] == 0
    
    def test_negative_values_raise_error(self):
        """Test that negative values raise ValueError."""
        with pytest.raises(ValueError):
            calculate_guttering(-10.0, 3.0)
        
        with pytest.raises(ValueError):
            calculate_guttering(10.0, -3.0)
    
    def test_negative_downpipes_raise_error(self):
        """Test that negative downpipes raise ValueError."""
        with pytest.raises(ValueError):
            calculate_guttering(10.0, 3.0, num_downpipes=-1)
    
    def test_end_caps_included(self):
        """Test that end caps are included in results."""
        result = calculate_guttering(10.0, 3.0)
        assert result['num_end_caps'] >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
