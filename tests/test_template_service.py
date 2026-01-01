"""
Tests for template service.
"""

import pytest
import sys
import os
import tempfile
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.template_models import CostEstimateTemplate
from app.services.template_service import TemplateManager


class TestTemplateService:
    """Tests for TemplateManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for templates."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create a TemplateManager with temporary directory."""
        return TemplateManager(templates_dir=temp_dir)
    
    def test_create_templates_dir(self, manager):
        """Test that templates directory is created."""
        assert os.path.exists(manager.templates_dir)
    
    def test_save_new_template(self, manager):
        """Test saving a new template."""
        items = [
            {'name': 'Item 1', 'quantity': 1.0, 'price': 100.0},
            {'name': 'Item 2', 'quantity': 2.0, 'price': 50.0}
        ]
        
        template = manager.save_template(
            name="Test Template",
            description="Test description",
            items=items,
            groups=["Materials", "Labor"]
        )
        
        assert template.id is not None
        assert template.name == "Test Template"
        assert template.description == "Test description"
        assert len(template.items) == 2
        assert len(template.groups) == 2
    
    def test_load_template(self, manager):
        """Test loading a saved template."""
        items = [{'name': 'Item 1', 'quantity': 1.0}]
        
        # Save template
        saved = manager.save_template(
            name="Load Test",
            description="Testing load",
            items=items
        )
        
        # Load template
        loaded = manager.load_template(saved.id)
        
        assert loaded is not None
        assert loaded.id == saved.id
        assert loaded.name == "Load Test"
        assert len(loaded.items) == 1
    
    def test_load_nonexistent_template(self, manager):
        """Test loading a template that doesn't exist."""
        result = manager.load_template("nonexistent-id")
        assert result is None
    
    def test_list_templates(self, manager):
        """Test listing all templates."""
        # Save multiple templates
        manager.save_template("Template 1", "Description 1", [])
        manager.save_template("Template 2", "Description 2", [])
        manager.save_template("Template 3", "Description 3", [])
        
        templates = manager.list_templates()
        
        assert len(templates) == 3
        # Should be sorted by updated date (most recent first)
        assert templates[0].name == "Template 3"
    
    def test_update_template(self, manager):
        """Test updating an existing template."""
        # Create initial template
        template = manager.save_template(
            name="Original Name",
            description="Original Description",
            items=[]
        )
        
        # Update template
        updated = manager.save_template(
            name="Updated Name",
            description="Updated Description",
            items=[{'name': 'New Item'}],
            template_id=template.id
        )
        
        assert updated.id == template.id
        assert updated.name == "Updated Name"
        assert len(updated.items) == 1
        # Creation date should be preserved
        assert updated.created_at == template.created_at
    
    def test_delete_template(self, manager):
        """Test deleting a template."""
        template = manager.save_template("To Delete", "Will be deleted", [])
        
        # Delete template
        result = manager.delete_template(template.id)
        assert result is True
        
        # Verify it's deleted
        loaded = manager.load_template(template.id)
        assert loaded is None
    
    def test_delete_nonexistent_template(self, manager):
        """Test deleting a template that doesn't exist."""
        result = manager.delete_template("nonexistent-id")
        assert result is False
    
    def test_export_template(self, manager, temp_dir):
        """Test exporting a template to a file."""
        template = manager.save_template("Export Test", "Testing export", [])
        
        export_path = os.path.join(temp_dir, "exported.json")
        result = manager.export_template(template.id, export_path)
        
        assert result is True
        assert os.path.exists(export_path)
    
    def test_import_template(self, manager, temp_dir):
        """Test importing a template from a file."""
        # Create and export a template
        template = manager.save_template("Import Test", "Testing import", [{'name': 'Test'}])
        export_path = os.path.join(temp_dir, "to_import.json")
        manager.export_template(template.id, export_path)
        
        # Import the template
        imported = manager.import_template(export_path)
        
        assert imported is not None
        assert imported.name == "Import Test"
        assert imported.id != template.id  # Should have new ID
        assert 'imported_from' in imported.metadata
    
    def test_search_templates(self, manager):
        """Test searching templates."""
        manager.save_template("Roof Materials", "Materials for roofing", [])
        manager.save_template("Door Installation", "Installing doors", [])
        manager.save_template("Window Materials", "Materials for windows", [])
        
        # Search by name
        results = manager.search_templates("materials")
        assert len(results) == 2
        
        # Search by description
        results = manager.search_templates("installing")
        assert len(results) == 1
        
        # No matches
        results = manager.search_templates("nonexistent")
        assert len(results) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
