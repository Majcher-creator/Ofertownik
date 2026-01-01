"""
Service for managing flashing profiles and calculations.
Similar to GutterSystemManager pattern.
"""

import json
import os
import uuid
from typing import List, Optional, Dict, Any

from app.models.flashing_models import FlashingProfile, FlashingMaterial


class FlashingManager:
    """
    Manages flashing profiles, materials, and calculations.
    """
    
    def __init__(self, config_path: str = "flashing_profiles.json"):
        """
        Initialize the flashing manager.
        
        Args:
            config_path: Path to the flashing profiles configuration file
        """
        self.config_path = config_path
        self.predefined_profiles: List[FlashingProfile] = []
        self.custom_profiles: List[FlashingProfile] = []
        self.materials: List[FlashingMaterial] = []
        self._load_config()
    
    def _load_config(self) -> None:
        """Load profiles and materials from configuration file."""
        if not os.path.exists(self.config_path):
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load predefined profiles
            predefined = data.get('predefined_profiles', [])
            self.predefined_profiles = [FlashingProfile.from_dict(p) for p in predefined]
            
            # Load custom profiles
            custom = data.get('custom_profiles', [])
            self.custom_profiles = [FlashingProfile.from_dict(p) for p in custom]
            
            # Load materials
            materials = data.get('materials', [])
            self.materials = [FlashingMaterial.from_dict(m) for m in materials]
            
        except Exception as e:
            print(f"Error loading flashing config: {e}")
            self.predefined_profiles = []
            self.custom_profiles = []
            self.materials = []
    
    def _create_default_config(self) -> None:
        """Create a default configuration file with common profiles."""
        default_config = {
            "predefined_profiles": [
                {
                    "id": "okap-standard",
                    "name": "Obróbka okapowa standard",
                    "description": "Standardowa obróbka okapu 250mm",
                    "development_width": 250.0,
                    "material_type": "stal",
                    "price_per_meter": 35.0,
                    "unit_conversions": {
                        "m2_per_meter": 0.25,
                        "kg_per_meter": 1.2
                    },
                    "is_custom": False
                },
                {
                    "id": "kalenica",
                    "name": "Kalenica prosta",
                    "description": "Obróbka kalenicy standard 500mm",
                    "development_width": 500.0,
                    "material_type": "stal",
                    "price_per_meter": 45.0,
                    "unit_conversions": {
                        "m2_per_meter": 0.5,
                        "kg_per_meter": 2.4
                    },
                    "is_custom": False
                },
                {
                    "id": "naroznik",
                    "name": "Narożnik zewnętrzny",
                    "description": "Obróbka narożnika zewnętrznego",
                    "development_width": 400.0,
                    "material_type": "stal",
                    "price_per_meter": 42.0,
                    "unit_conversions": {
                        "m2_per_meter": 0.4,
                        "kg_per_meter": 1.9
                    },
                    "is_custom": False
                },
                {
                    "id": "parapety",
                    "name": "Parapet zewnętrzny",
                    "description": "Obróbka parapetów",
                    "development_width": 300.0,
                    "material_type": "stal",
                    "price_per_meter": 38.0,
                    "unit_conversions": {
                        "m2_per_meter": 0.3,
                        "kg_per_meter": 1.4
                    },
                    "is_custom": False
                }
            ],
            "custom_profiles": [],
            "materials": [
                {
                    "id": "stal-polyester",
                    "name": "Blacha stalowa powlekana polyester",
                    "material_type": "stal",
                    "thickness_mm": 0.5,
                    "coating": "polyester",
                    "price_per_m2": 45.0,
                    "price_per_kg": 8.5,
                    "weight_per_m2": 4.8,
                    "color": "",
                    "supplier": ""
                },
                {
                    "id": "aluminium",
                    "name": "Blacha aluminiowa",
                    "material_type": "aluminium",
                    "thickness_mm": 0.7,
                    "coating": "anodowana",
                    "price_per_m2": 85.0,
                    "price_per_kg": 25.0,
                    "weight_per_m2": 1.9,
                    "color": "",
                    "supplier": ""
                },
                {
                    "id": "miedz",
                    "name": "Blacha miedziana naturalna",
                    "material_type": "miedź",
                    "thickness_mm": 0.6,
                    "coating": "naturalna",
                    "price_per_m2": 180.0,
                    "price_per_kg": 45.0,
                    "weight_per_m2": 5.4,
                    "color": "miedź",
                    "supplier": ""
                }
            ]
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating default flashing config: {e}")
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        config = {
            "predefined_profiles": [p.to_dict() for p in self.predefined_profiles],
            "custom_profiles": [p.to_dict() for p in self.custom_profiles],
            "materials": [m.to_dict() for m in self.materials]
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving flashing config: {e}")
    
    def get_all_profiles(self) -> List[FlashingProfile]:
        """Get all profiles (predefined + custom)."""
        return self.predefined_profiles + self.custom_profiles
    
    def get_profile_by_id(self, profile_id: str) -> Optional[FlashingProfile]:
        """Get a profile by ID."""
        for profile in self.get_all_profiles():
            if profile.id == profile_id:
                return profile
        return None
    
    def add_custom_profile(self, name: str, description: str, development_width: float,
                          material_type: str, price_per_meter: float,
                          unit_conversions: Optional[Dict[str, float]] = None) -> FlashingProfile:
        """
        Add a new custom profile.
        
        Returns:
            Created FlashingProfile
        """
        profile = FlashingProfile(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            development_width=development_width,
            material_type=material_type,
            price_per_meter=price_per_meter,
            unit_conversions=unit_conversions or {},
            is_custom=True
        )
        
        self.custom_profiles.append(profile)
        self._save_config()
        
        return profile
    
    def update_custom_profile(self, profile_id: str, **kwargs) -> bool:
        """Update a custom profile."""
        for i, profile in enumerate(self.custom_profiles):
            if profile.id == profile_id:
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                self._save_config()
                return True
        return False
    
    def delete_custom_profile(self, profile_id: str) -> bool:
        """Delete a custom profile."""
        for i, profile in enumerate(self.custom_profiles):
            if profile.id == profile_id:
                del self.custom_profiles[i]
                self._save_config()
                return True
        return False
    
    def get_material_by_id(self, material_id: str) -> Optional[FlashingMaterial]:
        """Get a material by ID."""
        for material in self.materials:
            if material.id == material_id:
                return material
        return None
    
    def add_material(self, name: str, material_type: str, thickness_mm: float,
                    coating: str, price_per_m2: float, **kwargs) -> FlashingMaterial:
        """Add a new material."""
        material = FlashingMaterial(
            id=str(uuid.uuid4()),
            name=name,
            material_type=material_type,
            thickness_mm=thickness_mm,
            coating=coating,
            price_per_m2=price_per_m2,
            **kwargs
        )
        
        self.materials.append(material)
        self._save_config()
        
        return material
    
    def calculate_sheet_requirements(self, profile_id: str, length_m: float) -> Dict[str, Any]:
        """
        Calculate material requirements for a flashing.
        
        Args:
            profile_id: Profile ID
            length_m: Required length in meters
            
        Returns:
            Dictionary with calculations
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        area_m2 = profile.calculate_area(length_m)
        weight_kg = profile.calculate_weight(length_m)
        total_price = length_m * profile.price_per_meter
        
        return {
            'profile_name': profile.name,
            'length_m': length_m,
            'area_m2': round(area_m2, 2),
            'weight_kg': round(weight_kg, 2),
            'price_per_meter': profile.price_per_meter,
            'total_price': round(total_price, 2)
        }
