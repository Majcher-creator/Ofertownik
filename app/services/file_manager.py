"""
File management service for loading and saving data files.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class FileManager:
    """
    Handles loading and saving of JSON files for the application.
    """
    
    @staticmethod
    def load_json(filepath: str, default: Any = None) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            default: Default value to return if file doesn't exist or is invalid
            
        Returns:
            Parsed JSON data or default value
        """
        if not os.path.exists(filepath):
            return default if default is not None else {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filepath}: {e}")
            return default if default is not None else {}
    
    @staticmethod
    def save_json(filepath: str, data: Any, indent: int = 2) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            filepath: Path to the JSON file
            data: Data to save
            indent: JSON indentation level
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except (IOError, TypeError) as e:
            print(f"Error saving {filepath}: {e}")
            return False
    
    @staticmethod
    def load_materials_database(filepath: str = "materialy_uslugi.json") -> List[Dict[str, Any]]:
        """
        Load materials and services database.
        
        Args:
            filepath: Path to the materials database file
            
        Returns:
            List of material/service dictionaries
        """
        data = FileManager.load_json(filepath, default=[])
        return data if isinstance(data, list) else []
    
    @staticmethod
    def save_materials_database(materials: List[Dict[str, Any]], 
                                filepath: str = "materialy_uslugi.json") -> bool:
        """
        Save materials and services database.
        
        Args:
            materials: List of material/service dictionaries
            filepath: Path to the materials database file
            
        Returns:
            True if successful, False otherwise
        """
        return FileManager.save_json(filepath, materials)
    
    @staticmethod
    def load_cost_estimate(filepath: str) -> Dict[str, Any]:
        """
        Load a cost estimate from file.
        
        Args:
            filepath: Path to the cost estimate file
            
        Returns:
            Dictionary containing cost estimate data
        """
        return FileManager.load_json(filepath, default={})
    
    @staticmethod
    def save_cost_estimate(data: Dict[str, Any], filepath: str) -> bool:
        """
        Save a cost estimate to file.
        
        Args:
            data: Cost estimate data
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        # Add metadata
        if 'metadata' not in data:
            data['metadata'] = {}
        data['metadata']['saved_at'] = datetime.now().isoformat()
        data['metadata']['version'] = '4.7.0'
        
        return FileManager.save_json(filepath, data)
    
    @staticmethod
    def load_settings(filepath: str = "settings.json") -> Dict[str, Any]:
        """
        Load application settings.
        
        Args:
            filepath: Path to settings file
            
        Returns:
            Dictionary containing settings
        """
        return FileManager.load_json(filepath, default={})
    
    @staticmethod
    def save_settings(settings: Dict[str, Any], filepath: str = "settings.json") -> bool:
        """
        Save application settings.
        
        Args:
            settings: Settings dictionary
            filepath: Path to settings file
            
        Returns:
            True if successful, False otherwise
        """
        return FileManager.save_json(filepath, settings)
