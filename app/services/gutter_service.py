"""
Service for managing gutter systems, templates, and configurations.
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.gutter_models import GutterSystem, GutterTemplate, GutterAccessory
from gutter_calculations import calculate_guttering


class GutterSystemManager:
    """Manages gutter systems, templates, and calculations."""
    
    def __init__(self, config_path: str = "gutter_systems.json"):
        """
        Initialize the manager.
        
        Args:
            config_path: Path to the gutter systems configuration file
        """
        self.config_path = config_path
        self.predefined_systems: List[GutterSystem] = []
        self.user_templates: List[GutterTemplate] = []
        self._load_systems()
    
    def _load_systems(self) -> None:
        """Load predefined systems and user templates from configuration file."""
        if not os.path.exists(self.config_path):
            # Create default config if it doesn't exist
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load predefined systems
            predefined = data.get('predefined_systems', [])
            self.predefined_systems = [GutterSystem.from_dict(sys) for sys in predefined]
            
            # Load user templates
            user_temps = data.get('user_templates', [])
            self.user_templates = [GutterTemplate.from_dict(temp) for temp in user_temps]
            
        except Exception as e:
            print(f"Error loading gutter systems: {e}")
            self.predefined_systems = []
            self.user_templates = []
    
    def _create_default_config(self) -> None:
        """Create a default configuration file with basic PVC system."""
        default_config = {
            "predefined_systems": [
                {
                    "name": "System PVC półokrągły 125mm",
                    "system_type": "pvc",
                    "description": "Podstawowy system PVC",
                    "accessories": [
                        {"name": "Rynna PVC 125mm", "unit": "mb", "price_unit_net": 25.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Rura spustowa PVC 90mm", "unit": "mb", "price_unit_net": 28.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Hak rynnowy PVC", "unit": "szt.", "price_unit_net": 8.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Łącznik rynny PVC", "unit": "szt.", "price_unit_net": 12.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Wylot do rury PVC", "unit": "szt.", "price_unit_net": 15.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Obejma rurowa PVC", "unit": "szt.", "price_unit_net": 10.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Kolano rury 67° PVC", "unit": "szt.", "price_unit_net": 18.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Zaślepka rynny PVC", "unit": "szt.", "price_unit_net": 6.0, "quantity": 0.0, "vat_rate": 8, "category": "material", "auto_calculate": True},
                        {"name": "Montaż systemu rynnowego", "unit": "mb", "price_unit_net": 15.0, "quantity": 0.0, "vat_rate": 8, "category": "service", "auto_calculate": True}
                    ]
                }
            ],
            "user_templates": []
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating default config: {e}")
    
    def save_systems(self) -> bool:
        """
        Save current systems and templates to configuration file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'predefined_systems': [sys.to_dict() for sys in self.predefined_systems],
                'user_templates': [temp.to_dict() for temp in self.user_templates]
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving gutter systems: {e}")
            return False
    
    def get_all_systems(self) -> List[GutterSystem]:
        """Get all predefined systems."""
        return self.predefined_systems.copy()
    
    def get_system_by_name(self, name: str) -> Optional[GutterSystem]:
        """
        Get a system by name.
        
        Args:
            name: Name of the system
            
        Returns:
            GutterSystem if found, None otherwise
        """
        for system in self.predefined_systems:
            if system.name == name:
                # Return a deep copy to avoid modifying the original
                return GutterSystem.from_dict(system.to_dict())
        return None
    
    def get_all_templates(self) -> List[GutterTemplate]:
        """Get all user templates."""
        return self.user_templates.copy()
    
    def save_user_template(self, template: GutterTemplate) -> bool:
        """
        Save a new user template or update existing one.
        
        Args:
            template: Template to save
            
        Returns:
            True if successful, False otherwise
        """
        # Check if template with same name exists
        for i, existing in enumerate(self.user_templates):
            if existing.name == template.name:
                self.user_templates[i] = template
                return self.save_systems()
        
        # Add new template
        template.created_at = datetime.now().isoformat()
        self.user_templates.append(template)
        return self.save_systems()
    
    def delete_user_template(self, template_name: str) -> bool:
        """
        Delete a user template.
        
        Args:
            template_name: Name of the template to delete
            
        Returns:
            True if successful, False otherwise
        """
        original_count = len(self.user_templates)
        self.user_templates = [t for t in self.user_templates if t.name != template_name]
        
        if len(self.user_templates) < original_count:
            return self.save_systems()
        return False
    
    def calculate_accessories(self, system: GutterSystem, okap_length_m: float, 
                            roof_height_m: float, num_downpipes: Optional[int] = None) -> GutterSystem:
        """
        Calculate accessory quantities for a gutter system based on roof parameters.
        
        Args:
            system: GutterSystem to calculate for
            okap_length_m: Total length of roof eaves in meters
            roof_height_m: Height of roof from eaves to ground in meters
            num_downpipes: Number of downpipes (if None, auto-calculated)
            
        Returns:
            GutterSystem with updated accessory quantities
        """
        # Use existing calculation function
        calc_results = calculate_guttering(okap_length_m, roof_height_m, num_downpipes)
        
        # Create a mapping of accessory types to calculated quantities
        quantity_map = {
            'rynna': calc_results['total_gutter_length_m'],
            'rura spustowa': calc_results['total_downpipe_length_m'],
            'hak': calc_results['num_gutter_hooks'],
            'łącznik': calc_results['num_gutter_connectors'],
            'wylot': calc_results['num_downpipe_outlets'],
            'obejma': calc_results['num_downpipe_clamps'],
            'kolano': calc_results['num_downpipe_elbows'],
            'zaślepka': calc_results['num_end_caps'],
            'montaż': calc_results['total_gutter_length_m']
        }
        
        # Update quantities for accessories that have auto_calculate=True
        for accessory in system.accessories:
            if accessory.auto_calculate:
                name_lower = accessory.name.lower()
                
                # Match accessory name to quantity
                for key, quantity in quantity_map.items():
                    if key in name_lower:
                        accessory.quantity = quantity
                        break
        
        return system
    
    def get_system_names(self) -> List[str]:
        """Get list of all system names."""
        return [sys.name for sys in self.predefined_systems]
    
    def get_template_names(self) -> List[str]:
        """Get list of all user template names."""
        return [temp.name for temp in self.user_templates]
