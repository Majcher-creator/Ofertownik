"""
Service for managing cost estimate templates.
"""

import json
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.template_models import CostEstimateTemplate


class TemplateManager:
    """
    Manages cost estimate templates - saving, loading, and organizing templates.
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Directory path for storing templates
        """
        self.templates_dir = templates_dir
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self) -> None:
        """Create templates directory if it doesn't exist."""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def _get_template_path(self, template_id: str) -> str:
        """Get file path for a template."""
        return os.path.join(self.templates_dir, f"{template_id}.json")
    
    def save_template(self, name: str, description: str, items: List[Dict[str, Any]],
                     groups: Optional[List[str]] = None, 
                     metadata: Optional[Dict[str, Any]] = None,
                     template_id: Optional[str] = None) -> CostEstimateTemplate:
        """
        Save a new template or update existing one.
        
        Args:
            name: Template name
            description: Template description
            items: List of cost items (as dictionaries)
            groups: List of group names
            metadata: Additional metadata
            template_id: Existing template ID (for updates), or None for new template
            
        Returns:
            Created or updated CostEstimateTemplate
        """
        now = datetime.now()
        
        if template_id is None:
            # Create new template
            template_id = str(uuid.uuid4())
            created_at = now
        else:
            # Update existing template - preserve creation date
            existing = self.load_template(template_id)
            created_at = existing.created_at if existing else now
        
        template = CostEstimateTemplate(
            id=template_id,
            name=name,
            description=description,
            created_at=created_at,
            updated_at=now,
            items=items,
            groups=groups or [],
            metadata=metadata or {}
        )
        
        # Save to file
        file_path = self._get_template_path(template_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
        
        return template
    
    def load_template(self, template_id: str) -> Optional[CostEstimateTemplate]:
        """
        Load a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            CostEstimateTemplate or None if not found
        """
        file_path = self._get_template_path(template_id)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return CostEstimateTemplate.from_dict(data)
        except Exception as e:
            print(f"Error loading template {template_id}: {e}")
            return None
    
    def list_templates(self) -> List[CostEstimateTemplate]:
        """
        List all available templates.
        
        Returns:
            List of CostEstimateTemplate objects
        """
        templates = []
        
        if not os.path.exists(self.templates_dir):
            return templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_id = filename[:-5]  # Remove .json extension
                template = self.load_template(template_id)
                if template:
                    templates.append(template)
        
        # Sort by updated date (most recent first)
        templates.sort(key=lambda t: t.updated_at, reverse=True)
        
        return templates
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        file_path = self._get_template_path(template_id)
        
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting template {template_id}: {e}")
            return False
    
    def export_template(self, template_id: str, export_path: str) -> bool:
        """
        Export a template to a file.
        
        Args:
            template_id: Template ID
            export_path: Path to export the template to
            
        Returns:
            True if exported successfully, False otherwise
        """
        template = self.load_template(template_id)
        if not template:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting template: {e}")
            return False
    
    def import_template(self, import_path: str) -> Optional[CostEstimateTemplate]:
        """
        Import a template from a file.
        
        Args:
            import_path: Path to the template file
            
        Returns:
            Imported CostEstimateTemplate or None if import failed
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Generate new ID for imported template to avoid conflicts
            old_id = data.get('id', '')
            data['id'] = str(uuid.uuid4())
            
            # Mark as imported in metadata
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['imported_from'] = old_id
            data['metadata']['imported_at'] = datetime.now().isoformat()
            
            template = CostEstimateTemplate.from_dict(data)
            
            # Save imported template
            file_path = self._get_template_path(template.id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
            
            return template
            
        except Exception as e:
            print(f"Error importing template: {e}")
            return None
    
    def search_templates(self, query: str) -> List[CostEstimateTemplate]:
        """
        Search templates by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching CostEstimateTemplate objects
        """
        all_templates = self.list_templates()
        query_lower = query.lower()
        
        matching = [
            t for t in all_templates
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]
        
        return matching
