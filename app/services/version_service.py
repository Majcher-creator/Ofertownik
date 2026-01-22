"""
Service for managing cost estimate versions and history.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from difflib import unified_diff

from app.models.version_models import Version, VersionHistory


class VersionManager:
    """
    Manages version control for cost estimates.
    Tracks changes, creates snapshots, and allows restoring previous versions.
    """
    
    def __init__(self, author: str = "User"):
        """
        Initialize the version manager.
        
        Args:
            author: Default author name for versions
        """
        self.author = author
        self.histories: Dict[str, VersionHistory] = {}
    
    def create_version(self, estimate_id: str, snapshot: Dict[str, Any],
                      description: Optional[str] = None,
                      auto_detect_changes: bool = True) -> Version:
        """
        Create a new version for an estimate.
        
        Args:
            estimate_id: Unique identifier for the estimate
            snapshot: Complete state of the estimate
            description: Optional description of changes
            auto_detect_changes: Whether to automatically detect changes
            
        Returns:
            Created Version object
        """
        # Get or create history
        if estimate_id not in self.histories:
            self.histories[estimate_id] = VersionHistory(estimate_id=estimate_id)
        
        history = self.histories[estimate_id]
        version_number = history.get_next_version_number()
        
        # Detect changes from previous version
        changes = []
        if auto_detect_changes and history.versions:
            previous_version = history.get_latest_version()
            if previous_version:
                changes = self._detect_changes(previous_version.snapshot, snapshot)
        
        # Generate description if not provided
        if description is None:
            if version_number == 1:
                description = "Wersja początkowa"
            else:
                description = f"Aktualizacja ({len(changes)} zmian)" if changes else "Zmodyfikowano"
        
        # Create version
        version = Version(
            id=str(uuid.uuid4()),
            version_number=version_number,
            created_at=datetime.now(),
            author=self.author,
            description=description,
            snapshot=snapshot,
            changes=changes
        )
        
        history.add_version(version)
        
        return version
    
    def get_history(self, estimate_id: str) -> Optional[VersionHistory]:
        """
        Get version history for an estimate.
        
        Args:
            estimate_id: Estimate identifier
            
        Returns:
            VersionHistory or None if not found
        """
        return self.histories.get(estimate_id)
    
    def get_version(self, estimate_id: str, version_number: int) -> Optional[Version]:
        """
        Get a specific version.
        
        Args:
            estimate_id: Estimate identifier
            version_number: Version number
            
        Returns:
            Version or None if not found
        """
        history = self.get_history(estimate_id)
        if history:
            return history.get_version(version_number)
        return None
    
    def restore_version(self, estimate_id: str, version_number: int) -> Optional[Dict[str, Any]]:
        """
        Restore an estimate to a previous version.
        
        Args:
            estimate_id: Estimate identifier
            version_number: Version number to restore
            
        Returns:
            Snapshot of the restored version, or None if not found
        """
        version = self.get_version(estimate_id, version_number)
        if version:
            return version.snapshot.copy()
        return None
    
    def compare_versions(self, estimate_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """
        Compare two versions and return differences.
        
        Args:
            estimate_id: Estimate identifier
            version1: First version number
            version2: Second version number
            
        Returns:
            Dictionary with comparison results
        """
        v1 = self.get_version(estimate_id, version1)
        v2 = self.get_version(estimate_id, version2)
        
        if not v1 or not v2:
            return {'error': 'Version not found'}
        
        changes = self._detect_changes(v1.snapshot, v2.snapshot)
        
        return {
            'version1': version1,
            'version2': version2,
            'changes': changes,
            'change_count': len(changes)
        }
    
    def _detect_changes(self, old_snapshot: Dict[str, Any], 
                       new_snapshot: Dict[str, Any]) -> List[str]:
        """
        Detect changes between two snapshots.
        
        Args:
            old_snapshot: Previous snapshot
            new_snapshot: New snapshot
            
        Returns:
            List of change descriptions
        """
        changes = []
        
        # Compare items
        old_items = old_snapshot.get('items', [])
        new_items = new_snapshot.get('items', [])
        
        if len(new_items) > len(old_items):
            diff = len(new_items) - len(old_items)
            changes.append(f"Dodano {diff} pozycji")
        elif len(new_items) < len(old_items):
            diff = len(old_items) - len(new_items)
            changes.append(f"Usunięto {diff} pozycji")
        
        # Compare totals
        old_total = old_snapshot.get('total_gross', 0)
        new_total = new_snapshot.get('total_gross', 0)
        
        if old_total != new_total:
            diff = new_total - old_total
            if diff > 0:
                changes.append(f"Zwiększono wartość o {diff:.2f} zł")
            else:
                changes.append(f"Zmniejszono wartość o {abs(diff):.2f} zł")
        
        # Compare other fields
        for key in ['client', 'title', 'notes']:
            if old_snapshot.get(key) != new_snapshot.get(key):
                changes.append(f"Zmieniono {key}")
        
        # Compare groups
        old_groups = set(old_snapshot.get('groups', []))
        new_groups = set(new_snapshot.get('groups', []))
        
        added_groups = new_groups - old_groups
        removed_groups = old_groups - new_groups
        
        if added_groups:
            changes.append(f"Dodano grupy: {', '.join(added_groups)}")
        if removed_groups:
            changes.append(f"Usunięto grupy: {', '.join(removed_groups)}")
        
        return changes
    
    def delete_version(self, estimate_id: str, version_number: int) -> bool:
        """
        Delete a specific version.
        
        Args:
            estimate_id: Estimate identifier
            version_number: Version number to delete
            
        Returns:
            True if deleted, False otherwise
        """
        history = self.get_history(estimate_id)
        if not history:
            return False
        
        # Don't delete the only version
        if len(history.versions) <= 1:
            return False
        
        # Don't delete the latest version
        latest = history.get_latest_version()
        if latest and latest.version_number == version_number:
            return False
        
        # Remove version
        history.versions = [v for v in history.versions if v.version_number != version_number]
        
        return True
    
    def prune_old_versions(self, estimate_id: str, keep_count: int = 10) -> int:
        """
        Remove old versions, keeping only the most recent ones.
        
        Args:
            estimate_id: Estimate identifier
            keep_count: Number of recent versions to keep
            
        Returns:
            Number of versions removed
        """
        history = self.get_history(estimate_id)
        if not history:
            return 0
        
        if len(history.versions) <= keep_count:
            return 0
        
        # Sort by version number and keep the most recent
        history.versions.sort(key=lambda v: v.version_number, reverse=True)
        to_remove = history.versions[keep_count:]
        history.versions = history.versions[:keep_count]
        
        return len(to_remove)
