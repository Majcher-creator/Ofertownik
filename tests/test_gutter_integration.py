"""
Integration tests for gutter system functionality.
Tests the complete workflow from system selection to cost estimate generation.
"""

import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.gutter_models import GutterAccessory, GutterSystem, GutterTemplate
from app.services.gutter_service import GutterSystemManager


class TestGutterWorkflow:
    """Integration tests for the complete gutter system workflow."""
    
    @pytest.fixture
    def manager_with_systems(self):
        """Create a manager with test systems."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        
        # Create test config
        config = {
            "predefined_systems": [
                {
                    "name": "Test PVC System",
                    "system_type": "pvc",
                    "description": "Test system",
                    "accessories": [
                        {
                            "name": "Rynna PVC 125mm",
                            "unit": "mb",
                            "price_unit_net": 25.0,
                            "quantity": 0.0,
                            "vat_rate": 8,
                            "category": "material",
                            "auto_calculate": True
                        },
                        {
                            "name": "Rura spustowa PVC 90mm",
                            "unit": "mb",
                            "price_unit_net": 28.0,
                            "quantity": 0.0,
                            "vat_rate": 8,
                            "category": "material",
                            "auto_calculate": True
                        },
                        {
                            "name": "Hak rynnowy PVC",
                            "unit": "szt.",
                            "price_unit_net": 8.0,
                            "quantity": 0.0,
                            "vat_rate": 8,
                            "category": "material",
                            "auto_calculate": True
                        },
                        {
                            "name": "Łącznik rynny PVC",
                            "unit": "szt.",
                            "price_unit_net": 12.0,
                            "quantity": 0.0,
                            "vat_rate": 8,
                            "category": "material",
                            "auto_calculate": True
                        },
                        {
                            "name": "Montaż systemu rynnowego",
                            "unit": "mb",
                            "price_unit_net": 15.0,
                            "quantity": 0.0,
                            "vat_rate": 8,
                            "category": "service",
                            "auto_calculate": True
                        }
                    ]
                }
            ],
            "user_templates": []
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        manager = GutterSystemManager(path)
        
        yield manager
        
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)
    
    def test_complete_workflow_with_calculation(self, manager_with_systems):
        """Test complete workflow: select system, calculate, add to cost estimate."""
        manager = manager_with_systems
        
        # Step 1: Select a system
        system = manager.get_system_by_name("Test PVC System")
        assert system is not None
        assert len(system.accessories) == 5
        
        # Step 2: Calculate accessories for roof parameters
        okap_length = 20.0  # 20 meters
        roof_height = 5.0    # 5 meters
        
        calculated_system = manager.calculate_accessories(system, okap_length, roof_height)
        
        # Step 3: Verify calculations
        rynna = calculated_system.get_accessory("Rynna PVC 125mm")
        assert rynna is not None
        assert rynna.quantity == 20.0  # Same as okap length
        
        hak = calculated_system.get_accessory("Hak rynnowy PVC")
        assert hak is not None
        assert hak.quantity == 40  # 20m / 0.5m = 40 hooks
        
        montaz = calculated_system.get_accessory("Montaż systemu rynnowego")
        assert montaz is not None
        assert montaz.quantity == 20.0  # Same as gutter length
        
        # Step 4: Simulate user editing an accessory
        result = calculated_system.update_accessory_quantity("Hak rynnowy PVC", 50)
        assert result is True
        
        updated_hak = calculated_system.get_accessory("Hak rynnowy PVC")
        assert updated_hak.quantity == 50
        
        # Step 5: Prepare items for cost estimate
        cost_items = []
        for acc in calculated_system.accessories:
            if acc.quantity > 0:
                cost_item = {
                    "name": acc.name,
                    "quantity": acc.quantity,
                    "unit": acc.unit,
                    "price_unit_net": acc.price_unit_net,
                    "vat_rate": acc.vat_rate,
                    "category": acc.category
                }
                cost_items.append(cost_item)
        
        # Verify cost items
        assert len(cost_items) == 5  # All accessories should have quantity > 0
        
        # Verify total calculation
        total_net = sum(item['quantity'] * item['price_unit_net'] for item in cost_items)
        assert total_net > 0
        
        # Expected approximate total for 20m system
        # Rynna: 20 * 25 = 500
        # Rura: 2 downpipes * 5m * 28 = 280
        # Haki: 50 * 8 = 400
        # Łączniki: ~6 * 12 = 72
        # Montaż: 20 * 15 = 300
        # Total: ~1552 PLN
        assert total_net > 1500
        assert total_net < 2000
    
    def test_workflow_with_template_save_and_load(self, manager_with_systems):
        """Test workflow with saving and loading custom template."""
        manager = manager_with_systems
        
        # Step 1: Get and customize a system
        system = manager.get_system_by_name("Test PVC System")
        calculated_system = manager.calculate_accessories(system, 25.0, 6.0)
        
        # Step 2: Customize prices
        rynna = calculated_system.get_accessory("Rynna PVC 125mm")
        rynna.price_unit_net = 30.0  # Custom price
        
        # Step 3: Save as template
        template = GutterTemplate(
            name="My Custom Configuration",
            system=calculated_system,
            is_predefined=False
        )
        
        result = manager.save_user_template(template)
        assert result is True
        
        # Step 4: Verify template was saved
        templates = manager.get_all_templates()
        assert len(templates) == 1
        assert templates[0].name == "My Custom Configuration"
        
        # Step 5: Reload manager to simulate app restart
        new_manager = GutterSystemManager(manager.config_path)
        
        # Step 6: Verify template persists
        loaded_templates = new_manager.get_all_templates()
        assert len(loaded_templates) == 1
        
        loaded_template = loaded_templates[0]
        assert loaded_template.name == "My Custom Configuration"
        
        # Verify custom price persists
        loaded_rynna = loaded_template.system.get_accessory("Rynna PVC 125mm")
        assert loaded_rynna.price_unit_net == 30.0
    
    def test_multiple_systems_selection(self, manager_with_systems):
        """Test switching between different gutter systems."""
        manager = manager_with_systems
        
        # Get system names
        system_names = manager.get_system_names()
        assert len(system_names) >= 1
        
        # Select first system
        system1 = manager.get_system_by_name(system_names[0])
        assert system1 is not None
        
        # Calculate for parameters
        calc1 = manager.calculate_accessories(system1, 15.0, 4.0)
        
        # Verify accessories are calculated
        accessories_with_qty = [acc for acc in calc1.accessories if acc.quantity > 0]
        assert len(accessories_with_qty) > 0
    
    def test_backward_compatibility(self):
        """Test that old calculation function still works."""
        from gutter_calculations import calculate_guttering
        
        # Old-style calculation should still work
        result = calculate_guttering(20.0, 5.0, num_downpipes=2)
        
        assert result['total_gutter_length_m'] == 20.0
        assert result['num_downpipes'] == 2
        assert result['total_downpipe_length_m'] == 10.0
        assert result['num_gutter_hooks'] == 40
    
    def test_manual_accessory_addition(self, manager_with_systems):
        """Test adding custom accessories manually."""
        manager = manager_with_systems
        
        # Get a system
        system = manager.get_system_by_name("Test PVC System")
        
        # Add a custom accessory
        custom_acc = GutterAccessory(
            name="Dodatkowy element",
            unit="szt.",
            price_unit_net=50.0,
            quantity=5.0,
            auto_calculate=False
        )
        
        system.accessories.append(custom_acc)
        
        # Calculate (custom accessory should keep its quantity)
        calculated = manager.calculate_accessories(system, 20.0, 5.0)
        
        custom = calculated.get_accessory("Dodatkowy element")
        assert custom is not None
        assert custom.quantity == 5.0  # Should not change since auto_calculate=False
    
    def test_edge_case_zero_parameters(self, manager_with_systems):
        """Test calculation with zero parameters."""
        manager = manager_with_systems
        
        system = manager.get_system_by_name("Test PVC System")
        
        # Calculate with zero okap length
        calculated = manager.calculate_accessories(system, 0.0, 5.0)
        
        rynna = calculated.get_accessory("Rynna PVC 125mm")
        assert rynna.quantity == 0.0
        
        hak = calculated.get_accessory("Hak rynnowy PVC")
        assert hak.quantity == 0
    
    def test_cost_estimate_generation(self, manager_with_systems):
        """Test generating cost estimate items with VAT calculations."""
        manager = manager_with_systems
        
        system = manager.get_system_by_name("Test PVC System")
        calculated = manager.calculate_accessories(system, 20.0, 5.0)
        
        # Generate cost items with calculations
        cost_items = []
        for acc in calculated.accessories:
            if acc.quantity > 0:
                total_net = acc.quantity * acc.price_unit_net
                vat_value = total_net * acc.vat_rate / 100.0
                total_gross = total_net + vat_value
                
                cost_item = {
                    "name": acc.name,
                    "quantity": acc.quantity,
                    "unit": acc.unit,
                    "price_unit_net": acc.price_unit_net,
                    "vat_rate": acc.vat_rate,
                    "total_net": round(total_net, 2),
                    "vat_value": round(vat_value, 2),
                    "total_gross": round(total_gross, 2)
                }
                cost_items.append(cost_item)
        
        # Verify all cost items have proper calculations
        for item in cost_items:
            assert item['total_net'] > 0
            assert item['vat_value'] > 0
            assert item['total_gross'] > item['total_net']
            assert abs(item['total_gross'] - (item['total_net'] + item['vat_value'])) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
