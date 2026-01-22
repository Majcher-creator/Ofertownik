"""
Tests for version service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.version_models import Version, VersionHistory
from app.services.version_service import VersionManager


class TestVersionService:
    """Tests for VersionManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a VersionManager."""
        return VersionManager(author="Test User")
    
    def test_create_first_version(self, manager):
        """Test creating the first version."""
        snapshot = {'items': [], 'total_gross': 0.0}
        
        version = manager.create_version("estimate-1", snapshot)
        
        assert version.version_number == 1
        assert version.author == "Test User"
        assert version.description == "Wersja początkowa"
        assert len(version.changes) == 0
    
    def test_create_multiple_versions(self, manager):
        """Test creating multiple versions."""
        # First version
        snapshot1 = {'items': [{'name': 'Item 1'}], 'total_gross': 100.0}
        v1 = manager.create_version("estimate-1", snapshot1)
        
        # Second version
        snapshot2 = {'items': [{'name': 'Item 1'}, {'name': 'Item 2'}], 'total_gross': 200.0}
        v2 = manager.create_version("estimate-1", snapshot2)
        
        assert v1.version_number == 1
        assert v2.version_number == 2
        assert len(v2.changes) > 0  # Should have detected changes
    
    def test_get_history(self, manager):
        """Test getting version history."""
        snapshot = {'items': []}
        manager.create_version("estimate-1", snapshot)
        
        history = manager.get_history("estimate-1")
        
        assert history is not None
        assert history.estimate_id == "estimate-1"
        assert len(history.versions) == 1
    
    def test_get_version(self, manager):
        """Test getting a specific version."""
        snapshot = {'items': [{'name': 'Item'}]}
        manager.create_version("estimate-1", snapshot)
        
        version = manager.get_version("estimate-1", 1)
        
        assert version is not None
        assert version.version_number == 1
        assert 'items' in version.snapshot
    
    def test_restore_version(self, manager):
        """Test restoring a previous version."""
        # Create multiple versions
        snapshot1 = {'items': [{'name': 'Item 1'}], 'total_gross': 100.0}
        snapshot2 = {'items': [{'name': 'Item 1'}, {'name': 'Item 2'}], 'total_gross': 200.0}
        
        manager.create_version("estimate-1", snapshot1)
        manager.create_version("estimate-1", snapshot2)
        
        # Restore to version 1
        restored = manager.restore_version("estimate-1", 1)
        
        assert restored is not None
        assert len(restored['items']) == 1
        assert restored['total_gross'] == 100.0
    
    def test_compare_versions(self, manager):
        """Test comparing two versions."""
        # Create versions with different content
        snapshot1 = {'items': [{'name': 'Item 1'}], 'total_gross': 100.0, 'groups': ['Group A']}
        snapshot2 = {'items': [{'name': 'Item 1'}, {'name': 'Item 2'}], 'total_gross': 200.0, 'groups': ['Group A', 'Group B']}
        
        manager.create_version("estimate-1", snapshot1)
        manager.create_version("estimate-1", snapshot2)
        
        # Compare versions
        comparison = manager.compare_versions("estimate-1", 1, 2)
        
        assert 'changes' in comparison
        assert 'change_count' in comparison
        assert comparison['change_count'] > 0
    
    def test_detect_changes_items(self, manager):
        """Test detection of item changes."""
        snapshot1 = {'items': [{'name': 'Item 1'}], 'total_gross': 100.0}
        snapshot2 = {'items': [{'name': 'Item 1'}, {'name': 'Item 2'}], 'total_gross': 100.0}
        
        manager.create_version("estimate-1", snapshot1)
        version = manager.create_version("estimate-1", snapshot2)
        
        # Should detect added item
        assert any('Dodano' in change for change in version.changes)
    
    def test_detect_changes_totals(self, manager):
        """Test detection of total value changes."""
        snapshot1 = {'items': [], 'total_gross': 100.0}
        snapshot2 = {'items': [], 'total_gross': 150.0}
        
        manager.create_version("estimate-1", snapshot1)
        version = manager.create_version("estimate-1", snapshot2)
        
        # Should detect value increase
        assert any('Zwiększono wartość' in change for change in version.changes)
    
    def test_detect_changes_groups(self, manager):
        """Test detection of group changes."""
        snapshot1 = {'items': [], 'groups': ['Group A']}
        snapshot2 = {'items': [], 'groups': ['Group A', 'Group B']}
        
        manager.create_version("estimate-1", snapshot1)
        version = manager.create_version("estimate-1", snapshot2)
        
        # Should detect added group
        assert any('Dodano grupy' in change for change in version.changes)
    
    def test_custom_description(self, manager):
        """Test creating version with custom description."""
        snapshot = {'items': []}
        
        version = manager.create_version("estimate-1", snapshot, description="Custom change description")
        
        assert version.description == "Custom change description"
    
    def test_delete_version(self, manager):
        """Test deleting a version."""
        snapshot = {'items': []}
        manager.create_version("estimate-1", snapshot)
        manager.create_version("estimate-1", snapshot)
        manager.create_version("estimate-1", snapshot)
        
        # Try to delete middle version
        result = manager.delete_version("estimate-1", 2)
        
        assert result is True
        history = manager.get_history("estimate-1")
        assert len(history.versions) == 2
    
    def test_cannot_delete_only_version(self, manager):
        """Test that you cannot delete the only version."""
        snapshot = {'items': []}
        manager.create_version("estimate-1", snapshot)
        
        result = manager.delete_version("estimate-1", 1)
        
        assert result is False
    
    def test_cannot_delete_latest_version(self, manager):
        """Test that you cannot delete the latest version."""
        snapshot = {'items': []}
        manager.create_version("estimate-1", snapshot)
        manager.create_version("estimate-1", snapshot)
        
        result = manager.delete_version("estimate-1", 2)
        
        assert result is False
    
    def test_prune_old_versions(self, manager):
        """Test pruning old versions."""
        snapshot = {'items': []}
        
        # Create many versions
        for i in range(15):
            manager.create_version("estimate-1", snapshot)
        
        # Prune to keep only 10
        removed_count = manager.prune_old_versions("estimate-1", keep_count=10)
        
        assert removed_count == 5
        history = manager.get_history("estimate-1")
        assert len(history.versions) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
