"""
Unit tests for gutter models and service.
"""

import pytest
import sys
import os
import json
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.gutter_models import GutterAccessory, GutterSystem, GutterTemplate
from app.services.gutter_service import GutterSystemManager


class TestGutterAccessory:
    """Tests for GutterAccessory model."""
    
    def test_create_accessory(self):
        """Test creating a gutter accessory."""
        acc = GutterAccessory(
            name="Rynna PVC",
            unit="mb",
            price_unit_net=25.0,
            quantity=10.0
        )
        
        assert acc.name == "Rynna PVC"
        assert acc.unit == "mb"
        assert acc.price_unit_net == 25.0
        assert acc.quantity == 10.0
        assert acc.vat_rate == 8
        assert acc.auto_calculate is True
    
    def test_accessory_to_dict(self):
        """Test converting accessory to dictionary."""
        acc = GutterAccessory(name="Test", unit="szt.", price_unit_net=10.0)
        data = acc.to_dict()
        
        assert isinstance(data, dict)
        assert data['name'] == "Test"
        assert data['unit'] == "szt."
        assert data['price_unit_net'] == 10.0
    
    def test_accessory_from_dict(self):
        """Test creating accessory from dictionary."""
        data = {
            'name': 'Hak rynnowy',
            'unit': 'szt.',
            'price_unit_net': 8.0,
            'quantity': 20.0,
            'vat_rate': 8,
            'category': 'material',
            'auto_calculate': True
        }
        
        acc = GutterAccessory.from_dict(data)
        
        assert acc.name == 'Hak rynnowy'
        assert acc.quantity == 20.0
        assert acc.vat_rate == 8


class TestGutterSystem:
    """Tests for GutterSystem model."""
    
    def test_create_system(self):
        """Test creating a gutter system."""
        acc1 = GutterAccessory(name="Rynna", unit="mb", price_unit_net=25.0)
        acc2 = GutterAccessory(name="Hak", unit="szt.", price_unit_net=8.0)
        
        system = GutterSystem(
            name="System PVC",
            system_type="pvc",
            description="Test system",
            accessories=[acc1, acc2]
        )
        
        assert system.name == "System PVC"
        assert system.system_type == "pvc"
        assert len(system.accessories) == 2
    
    def test_system_to_dict(self):
        """Test converting system to dictionary."""
        acc = GutterAccessory(name="Rynna", unit="mb", price_unit_net=25.0)
        system = GutterSystem(name="Test", system_type="pvc", accessories=[acc])
        
        data = system.to_dict()
        
        assert isinstance(data, dict)
        assert data['name'] == "Test"
        assert data['system_type'] == "pvc"
        assert len(data['accessories']) == 1
    
    def test_system_from_dict(self):
        """Test creating system from dictionary."""
        data = {
            'name': 'PVC System',
            'system_type': 'pvc',
            'description': 'Test',
            'accessories': [
                {'name': 'Rynna', 'unit': 'mb', 'price_unit_net': 25.0, 'quantity': 0.0, 'vat_rate': 8, 'category': 'material', 'auto_calculate': True}
            ]
        }
        
        system = GutterSystem.from_dict(data)
        
        assert system.name == 'PVC System'
        assert len(system.accessories) == 1
        assert system.accessories[0].name == 'Rynna'
    
    def test_get_accessory(self):
        """Test getting accessory by name."""
        acc1 = GutterAccessory(name="Rynna", unit="mb", price_unit_net=25.0)
        acc2 = GutterAccessory(name="Hak", unit="szt.", price_unit_net=8.0)
        system = GutterSystem(name="Test", system_type="pvc", accessories=[acc1, acc2])
        
        found = system.get_accessory("Hak")
        assert found is not None
        assert found.name == "Hak"
        
        not_found = system.get_accessory("Nonexistent")
        assert not_found is None
    
    def test_update_accessory_quantity(self):
        """Test updating accessory quantity."""
        acc = GutterAccessory(name="Rynna", unit="mb", price_unit_net=25.0, quantity=0.0)
        system = GutterSystem(name="Test", system_type="pvc", accessories=[acc])
        
        result = system.update_accessory_quantity("Rynna", 15.5)
        assert result is True
        assert system.get_accessory("Rynna").quantity == 15.5
        
        result = system.update_accessory_quantity("Nonexistent", 10.0)
        assert result is False


class TestGutterTemplate:
    """Tests for GutterTemplate model."""
    
    def test_create_template(self):
        """Test creating a gutter template."""
        system = GutterSystem(name="Test System", system_type="pvc")
        template = GutterTemplate(
            name="My Template",
            system=system,
            is_predefined=False
        )
        
        assert template.name == "My Template"
        assert template.system.name == "Test System"
        assert template.is_predefined is False
    
    def test_template_to_dict(self):
        """Test converting template to dictionary."""
        system = GutterSystem(name="Test", system_type="pvc")
        template = GutterTemplate(name="Template1", system=system)
        
        data = template.to_dict()
        
        assert isinstance(data, dict)
        assert data['name'] == "Template1"
        assert 'system' in data
    
    def test_template_from_dict(self):
        """Test creating template from dictionary."""
        data = {
            'name': 'Template1',
            'system': {
                'name': 'Test System',
                'system_type': 'pvc',
                'description': '',
                'accessories': []
            },
            'is_predefined': True,
            'created_at': '2024-01-01T00:00:00'
        }
        
        template = GutterTemplate.from_dict(data)
        
        assert template.name == 'Template1'
        assert template.system.name == 'Test System'
        assert template.is_predefined is True


class TestGutterSystemManager:
    """Tests for GutterSystemManager service."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        
        # Create a minimal config
        config = {
            "predefined_systems": [
                {
                    "name": "Test PVC System",
                    "system_type": "pvc",
                    "description": "Test",
                    "accessories": [
                        {"name": "Rynna", "unit": "mb", "price_unit_net": 25.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Hak", "unit": "szt.", "price_unit_net": 8.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True}
                    ]
                }
            ],
            "user_templates": []
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        yield path
        
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)
    
    def test_manager_initialization(self, temp_config_file):
        """Test initializing the manager."""
        manager = GutterSystemManager(temp_config_file)
        
        assert len(manager.predefined_systems) == 1
        assert manager.predefined_systems[0].name == "Test PVC System"
        assert len(manager.user_templates) == 0
    
    def test_get_all_systems(self, temp_config_file):
        """Test getting all systems."""
        manager = GutterSystemManager(temp_config_file)
        systems = manager.get_all_systems()
        
        assert len(systems) == 1
        assert systems[0].name == "Test PVC System"
    
    def test_get_system_by_name(self, temp_config_file):
        """Test getting system by name."""
        manager = GutterSystemManager(temp_config_file)
        
        system = manager.get_system_by_name("Test PVC System")
        assert system is not None
        assert system.name == "Test PVC System"
        
        not_found = manager.get_system_by_name("Nonexistent")
        assert not_found is None
    
    def test_save_user_template(self, temp_config_file):
        """Test saving a user template."""
        manager = GutterSystemManager(temp_config_file)
        
        system = GutterSystem(name="Custom System", system_type="steel")
        template = GutterTemplate(name="My Custom Template", system=system)
        
        result = manager.save_user_template(template)
        assert result is True
        assert len(manager.user_templates) == 1
        assert manager.user_templates[0].name == "My Custom Template"
    
    def test_delete_user_template(self, temp_config_file):
        """Test deleting a user template."""
        manager = GutterSystemManager(temp_config_file)
        
        # Add a template
        system = GutterSystem(name="Custom", system_type="steel")
        template = GutterTemplate(name="To Delete", system=system)
        manager.save_user_template(template)
        
        # Delete it
        result = manager.delete_user_template("To Delete")
        assert result is True
        assert len(manager.user_templates) == 0
    
    def test_calculate_accessories(self, temp_config_file):
        """Test calculating accessory quantities."""
        manager = GutterSystemManager(temp_config_file)
        
        system = manager.get_system_by_name("Test PVC System")
        assert system is not None
        
        # Calculate for 20m eaves, 5m height
        updated_system = manager.calculate_accessories(system, 20.0, 5.0)
        
        # Check that quantities were updated
        rynna = updated_system.get_accessory("Rynna")
        assert rynna is not None
        assert rynna.quantity == 20.0  # Total gutter length
        
        hak = updated_system.get_accessory("Hak")
        assert hak is not None
        assert hak.quantity == 40  # 20m / 0.5m = 40 hooks
    
    def test_get_system_names(self, temp_config_file):
        """Test getting system names."""
        manager = GutterSystemManager(temp_config_file)
        names = manager.get_system_names()
        
        assert len(names) == 1
        assert "Test PVC System" in names
    
    def test_get_template_names(self, temp_config_file):
        """Test getting template names."""
        manager = GutterSystemManager(temp_config_file)
        
        # Add a template
        system = GutterSystem(name="Custom", system_type="steel")
        template = GutterTemplate(name="Template1", system=system)
        manager.save_user_template(template)
        
        names = manager.get_template_names()
        assert len(names) == 1
        assert "Template1" in names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
