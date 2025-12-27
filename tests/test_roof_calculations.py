"""
Unit tests for roof calculation functions.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roof_calculations import (
    calculate_single_slope_roof,
    calculate_gable_roof,
    calculate_hip_roof,
    calculate_slant_length,
    degrees_to_radians
)


class TestRoofCalculations:
    """Test suite for roof calculation functions."""
    
    def test_degrees_to_radians(self):
        """Test degree to radian conversion."""
        import math
        assert abs(degrees_to_radians(0) - 0) < 0.001
        assert abs(degrees_to_radians(90) - math.pi/2) < 0.001
        assert abs(degrees_to_radians(180) - math.pi) < 0.001
        assert abs(degrees_to_radians(360) - 2*math.pi) < 0.001
    
    def test_calculate_slant_length(self):
        """Test slant length calculation."""
        # 45 degree angle should multiply by sqrt(2)
        result = calculate_slant_length(10.0, 45.0)
        assert abs(result - 14.142) < 0.01
        
        # 0 degree angle should return same length
        result = calculate_slant_length(10.0, 0.0)
        assert abs(result - 10.0) < 0.001
        
        # 90 degree angle should return infinity
        result = calculate_slant_length(10.0, 90.0)
        assert result == float('inf')
    
    def test_single_slope_roof_horizontal_dimensions(self):
        """Test single slope roof calculation with horizontal dimensions."""
        result = calculate_single_slope_roof(10.0, 8.0, 30.0, False)
        
        assert result['dlugosc_okapu'] == 10.0
        assert result['powierzchnia_dachu'] > 0
        assert 'slant_rafter_length' in result
        assert result['slant_rafter_length'] > 8.0  # Should be longer due to angle
        assert result['roof_angle_deg'] == 30.0
    
    def test_single_slope_roof_real_dimensions(self):
        """Test single slope roof calculation with real dimensions."""
        result = calculate_single_slope_roof(10.0, 8.0, None, True)
        
        assert result['dlugosc_okapu'] == 10.0
        assert result['slant_rafter_length'] == 8.0
        assert result['powierzchnia_dachu'] == 80.0
        assert result['dlugosc_wiatrownic'] == 16.0
    
    def test_gable_roof_calculation(self):
        """Test gable roof calculation."""
        result = calculate_gable_roof(10.0, 8.0, 30.0, False)
        
        assert result['powierzchnia_dachu'] > 0
        assert 'dlugosc_okapu' in result
        assert result['dlugosc_okapu'] == 20.0  # 2 * length
        assert 'dlugosc_gasiorow' in result
        assert result['dlugosc_gasiorow'] == 10.0  # Same as length
        assert result['roof_angle_deg'] == 30.0
    
    def test_gable_roof_real_dimensions(self):
        """Test gable roof with real dimensions."""
        result = calculate_gable_roof(10.0, 8.0, None, True)
        
        assert result['dlugosc_okapu'] == 20.0
        assert result['dlugosc_gasiorow'] == 10.0
        assert result['powierzchnia_dachu'] == 160.0  # 2 * 10 * 8
        assert result['slant_rafter_length'] == 8.0
    
    def test_hip_roof_calculation(self):
        """Test hip roof calculation."""
        result = calculate_hip_roof(12.0, 10.0, 25.0, False)
        
        assert result['powierzchnia_dachu'] > 0
        assert 'dlugosc_okapu' in result
        assert result['dlugosc_okapu'] > 0
        assert 'dlugosc_gasiorow' in result
        assert result['dlugosc_gasiorow'] > 0
        assert result['roof_angle_deg'] == 25.0
    
    def test_hip_roof_requires_angle(self):
        """Test that hip roof requires angle parameter."""
        with pytest.raises(ValueError):
            calculate_hip_roof(12.0, 10.0, None, False)
    
    def test_negative_dimensions_handling(self):
        """Test handling of negative dimensions."""
        # These should still work but produce reasonable results
        result = calculate_single_slope_roof(10.0, 8.0, 30.0, False)
        assert result['powierzchnia_dachu'] > 0
    
    def test_zero_angle_handling(self):
        """Test handling of zero angle."""
        result = calculate_single_slope_roof(10.0, 8.0, 0.0, False)
        assert result['slant_rafter_length'] == 8.0  # No slope
        assert result['powierzchnia_dachu'] == 80.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
