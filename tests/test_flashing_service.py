"""
Tests for flashing service.
"""

import pytest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.flashing_models import FlashingProfile, FlashingMaterial
from app.services.flashing_service import FlashingManager


class TestFlashingService:
    """Tests for FlashingManager class."""
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary config file."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)
    
    @pytest.fixture
    def manager(self, temp_config):
        """Create a FlashingManager with temporary config."""
        return FlashingManager(config_path=temp_config)
    
    def test_creates_default_config(self, manager):
        """Test that default config is created."""
        assert os.path.exists(manager.config_path)
        assert len(manager.predefined_profiles) > 0
        assert len(manager.materials) > 0
    
    def test_get_all_profiles(self, manager):
        """Test getting all profiles."""
        profiles = manager.get_all_profiles()
        
        assert len(profiles) > 0
        # Should include predefined profiles
        assert any(p.name == "Obróbka okapowa standard" for p in profiles)
    
    def test_get_profile_by_id(self, manager):
        """Test getting a specific profile by ID."""
        profile = manager.get_profile_by_id("okap-standard")
        
        assert profile is not None
        assert profile.name == "Obróbka okapowa standard"
        assert profile.material_type == "stal"
    
    def test_add_custom_profile(self, manager):
        """Test adding a custom profile."""
        profile = manager.add_custom_profile(
            name="Custom Profile",
            description="Test custom profile",
            development_width=350.0,
            material_type="aluminium",
            price_per_meter=55.0,
            unit_conversions={"m2_per_meter": 0.35, "kg_per_meter": 1.5}
        )
        
        assert profile.id is not None
        assert profile.is_custom is True
        assert profile.name == "Custom Profile"
        
        # Verify it's saved
        loaded = manager.get_profile_by_id(profile.id)
        assert loaded is not None
        assert loaded.name == "Custom Profile"
    
    def test_update_custom_profile(self, manager):
        """Test updating a custom profile."""
        # Create profile
        profile = manager.add_custom_profile(
            name="Original Name",
            description="Original description",
            development_width=300.0,
            material_type="stal",
            price_per_meter=40.0
        )
        
        # Update profile
        result = manager.update_custom_profile(
            profile.id,
            name="Updated Name",
            price_per_meter=45.0
        )
        
        assert result is True
        
        # Verify update
        updated = manager.get_profile_by_id(profile.id)
        assert updated.name == "Updated Name"
        assert updated.price_per_meter == 45.0
    
    def test_delete_custom_profile(self, manager):
        """Test deleting a custom profile."""
        # Create profile
        profile = manager.add_custom_profile(
            name="To Delete",
            description="Will be deleted",
            development_width=300.0,
            material_type="stal",
            price_per_meter=40.0
        )
        
        # Delete profile
        result = manager.delete_custom_profile(profile.id)
        
        assert result is True
        
        # Verify deletion
        deleted = manager.get_profile_by_id(profile.id)
        assert deleted is None
    
    def test_get_material_by_id(self, manager):
        """Test getting a material by ID."""
        material = manager.get_material_by_id("stal-polyester")
        
        assert material is not None
        assert material.name == "Blacha stalowa powlekana polyester"
        assert material.material_type == "stal"
    
    def test_add_material(self, manager):
        """Test adding a new material."""
        material = manager.add_material(
            name="Test Material",
            material_type="aluminium",
            thickness_mm=0.8,
            coating="anodowana",
            price_per_m2=95.0,
            color="srebrny"
        )
        
        assert material.id is not None
        assert material.name == "Test Material"
        
        # Verify it's saved
        loaded = manager.get_material_by_id(material.id)
        assert loaded is not None
    
    def test_calculate_sheet_requirements(self, manager):
        """Test calculating sheet requirements."""
        result = manager.calculate_sheet_requirements("okap-standard", 10.0)
        
        assert 'profile_name' in result
        assert 'length_m' in result
        assert 'area_m2' in result
        assert 'weight_kg' in result
        assert 'total_price' in result
        
        assert result['length_m'] == 10.0
        assert result['area_m2'] > 0
        assert result['total_price'] > 0
    
    def test_profile_calculate_area(self):
        """Test FlashingProfile area calculation."""
        profile = FlashingProfile(
            id="test",
            name="Test",
            description="Test profile",
            development_width=300.0,
            material_type="stal",
            price_per_meter=40.0,
            unit_conversions={"m2_per_meter": 0.3, "kg_per_meter": 1.4}
        )
        
        area = profile.calculate_area(10.0)
        
        assert area == 3.0  # 10m * 0.3 m²/m
    
    def test_profile_calculate_weight(self):
        """Test FlashingProfile weight calculation."""
        profile = FlashingProfile(
            id="test",
            name="Test",
            description="Test profile",
            development_width=300.0,
            material_type="stal",
            price_per_meter=40.0,
            unit_conversions={"m2_per_meter": 0.3, "kg_per_meter": 1.4}
        )
        
        weight = profile.calculate_weight(10.0)
        
        assert weight == 14.0  # 10m * 1.4 kg/m
    
    def test_material_calculate_price_by_area(self):
        """Test FlashingMaterial price calculation by area."""
        material = FlashingMaterial(
            id="test",
            name="Test Material",
            material_type="stal",
            thickness_mm=0.5,
            coating="polyester",
            price_per_m2=50.0
        )
        
        price = material.calculate_price_by_area(5.0)
        
        assert price == 250.0  # 5 m² * 50 zł/m²
    
    def test_material_calculate_price_by_weight(self):
        """Test FlashingMaterial price calculation by weight."""
        material = FlashingMaterial(
            id="test",
            name="Test Material",
            material_type="aluminium",
            thickness_mm=0.7,
            coating="anodowana",
            price_per_m2=85.0,
            price_per_kg=25.0
        )
        
        price = material.calculate_price_by_weight(10.0)
        
        assert price == 250.0  # 10 kg * 25 zł/kg


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
