"""
History model for cost estimate versioning.
Tracks changes to cost estimates with snapshots and metadata.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import copy
import hashlib
import json


@dataclass
class HistoryEntry:
    """
    Represents a single version in cost estimate history.
    """
    timestamp: str
    version: int
    description: str
    items_count: int
    total_gross: float
    checksum: str  # MD5 hash of items for change detection
    items_snapshot: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history entry to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create HistoryEntry from dictionary."""
        return cls(
            timestamp=data.get('timestamp', ''),
            version=data.get('version', 0),
            description=data.get('description', ''),
            items_count=data.get('items_count', 0),
            total_gross=data.get('total_gross', 0.0),
            checksum=data.get('checksum', ''),
            items_snapshot=data.get('items_snapshot', []),
            metadata=data.get('metadata', {})
        )


class CostEstimateHistory:
    """
    Manages versioned history of a cost estimate.
    Stores snapshots of cost estimate states for version control.
    """
    
    MAX_HISTORY_ENTRIES = 50
    
    def __init__(self):
        """Initialize empty history."""
        self._entries: List[HistoryEntry] = []
        self._current_version = 0
    
    def add_entry(self, description: str, items: List[Dict[str, Any]], 
                  metadata: Optional[Dict[str, Any]] = None) -> HistoryEntry:
        """
        Add a new history entry.
        
        Args:
            description: Description of this version
            items: List of cost items
            metadata: Additional metadata (client, transport, etc.)
            
        Returns:
            The created HistoryEntry
        """
        # Calculate totals
        total_gross = sum(item.get('total_gross', 0.0) for item in items)
        items_count = len(items)
        
        # Calculate checksum
        checksum = self.calculate_checksum(items)
        
        # Create entry
        self._current_version += 1
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            version=self._current_version,
            description=description,
            items_count=items_count,
            total_gross=total_gross,
            checksum=checksum,
            items_snapshot=copy.deepcopy(items),
            metadata=copy.deepcopy(metadata) if metadata else {}
        )
        
        # Add to history
        self._entries.append(entry)
        
        # Limit history size
        if len(self._entries) > self.MAX_HISTORY_ENTRIES:
            self._entries.pop(0)
            # Renumber versions
            for i, e in enumerate(self._entries, 1):
                e.version = i
            self._current_version = len(self._entries)
        
        return entry
    
    def get_entry(self, version: int) -> Optional[HistoryEntry]:
        """
        Get a specific history entry by version number.
        
        Args:
            version: Version number to retrieve
            
        Returns:
            HistoryEntry or None if not found
        """
        for entry in self._entries:
            if entry.version == version:
                return entry
        return None
    
    def get_latest(self) -> Optional[HistoryEntry]:
        """
        Get the most recent history entry.
        
        Returns:
            Latest HistoryEntry or None if history is empty
        """
        return self._entries[-1] if self._entries else None
    
    def get_all_entries(self) -> List[HistoryEntry]:
        """
        Get all history entries.
        
        Returns:
            List of all HistoryEntry objects
        """
        return self._entries.copy()
    
    def compare_versions(self, version1: int, version2: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare two versions and return differences.
        
        Args:
            version1: First version to compare
            version2: Second version to compare
            
        Returns:
            Dictionary with 'added', 'removed', and 'changed' items
        """
        entry1 = self.get_entry(version1)
        entry2 = self.get_entry(version2)
        
        if not entry1 or not entry2:
            return {'added': [], 'removed': [], 'changed': []}
        
        items1 = {self._item_key(item): item for item in entry1.items_snapshot}
        items2 = {self._item_key(item): item for item in entry2.items_snapshot}
        
        # Find added items
        added = [items2[key] for key in items2 if key not in items1]
        
        # Find removed items
        removed = [items1[key] for key in items1 if key not in items2]
        
        # Find changed items
        changed = []
        for key in items1:
            if key in items2:
                if self._items_differ(items1[key], items2[key]):
                    changed.append({
                        'old': items1[key],
                        'new': items2[key]
                    })
        
        return {
            'added': added,
            'removed': removed,
            'changed': changed
        }
    
    def clear(self):
        """Clear all history entries."""
        self._entries = []
        self._current_version = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert history to dictionary for serialization.
        
        Returns:
            Dictionary representation of history
        """
        return {
            'current_version': self._current_version,
            'entries': [entry.to_dict() for entry in self._entries]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CostEstimateHistory':
        """
        Create history from dictionary.
        
        Args:
            data: Dictionary containing history data
            
        Returns:
            CostEstimateHistory instance
        """
        history = cls()
        history._current_version = data.get('current_version', 0)
        history._entries = [
            HistoryEntry.from_dict(entry_data)
            for entry_data in data.get('entries', [])
        ]
        return history
    
    @staticmethod
    def calculate_checksum(items: List[Dict[str, Any]]) -> str:
        """
        Calculate MD5 checksum of items for change detection.
        
        Args:
            items: List of cost items
            
        Returns:
            MD5 hash string
        """
        # Create a stable string representation
        items_str = json.dumps(items, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(items_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _item_key(item: Dict[str, Any]) -> str:
        """Generate a unique key for an item based on name and unit."""
        return f"{item.get('name', '')}_{item.get('unit', '')}"
    
    @staticmethod
    def _items_differ(item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """Check if two items differ in any significant way."""
        keys_to_compare = ['quantity', 'price_unit_net', 'vat_rate', 'category']
        for key in keys_to_compare:
            if item1.get(key) != item2.get(key):
                return True
        return False
