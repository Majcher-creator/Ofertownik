"""
Tests for the cost estimate history model.
"""

import pytest
from datetime import datetime
from app.models.history import HistoryEntry, CostEstimateHistory


class TestHistoryEntry:
    """Tests for HistoryEntry dataclass."""
    
    def test_history_entry_creation(self):
        """Test creating a history entry."""
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            version=1,
            description="Initial version",
            items_count=5,
            total_gross=1000.0,
            checksum="abc123",
            items_snapshot=[{"name": "Item 1"}],
            metadata={"client": "Test Client"}
        )
        
        assert entry.version == 1
        assert entry.description == "Initial version"
        assert entry.items_count == 5
        assert entry.total_gross == 1000.0
        
    def test_history_entry_to_dict(self):
        """Test converting history entry to dictionary."""
        entry = HistoryEntry(
            timestamp="2024-01-01T12:00:00",
            version=1,
            description="Test",
            items_count=3,
            total_gross=500.0,
            checksum="xyz",
            items_snapshot=[],
            metadata={}
        )
        
        data = entry.to_dict()
        assert data['version'] == 1
        assert data['description'] == "Test"
        assert data['items_count'] == 3
        
    def test_history_entry_from_dict(self):
        """Test creating history entry from dictionary."""
        data = {
            'timestamp': '2024-01-01T12:00:00',
            'version': 2,
            'description': 'Test from dict',
            'items_count': 10,
            'total_gross': 2000.0,
            'checksum': 'abc',
            'items_snapshot': [{'name': 'Item'}],
            'metadata': {'key': 'value'}
        }
        
        entry = HistoryEntry.from_dict(data)
        assert entry.version == 2
        assert entry.description == 'Test from dict'
        assert entry.items_count == 10


class TestCostEstimateHistory:
    """Tests for CostEstimateHistory class."""
    
    def test_history_initialization(self):
        """Test creating history instance."""
        history = CostEstimateHistory()
        assert len(history.get_all_entries()) == 0
        assert history.get_latest() is None
        
    def test_add_entry(self):
        """Test adding entry to history."""
        history = CostEstimateHistory()
        items = [
            {'name': 'Item 1', 'quantity': 10, 'total_gross': 100.0},
            {'name': 'Item 2', 'quantity': 5, 'total_gross': 50.0}
        ]
        
        entry = history.add_entry("First save", items)
        
        assert entry.version == 1
        assert entry.items_count == 2
        assert entry.total_gross == 150.0
        assert len(history.get_all_entries()) == 1
        
    def test_add_multiple_entries(self):
        """Test adding multiple entries."""
        history = CostEstimateHistory()
        items1 = [{'name': 'Item 1', 'total_gross': 100.0}]
        items2 = [{'name': 'Item 2', 'total_gross': 200.0}]
        items3 = [{'name': 'Item 3', 'total_gross': 300.0}]
        
        history.add_entry("First", items1)
        history.add_entry("Second", items2)
        history.add_entry("Third", items3)
        
        assert len(history.get_all_entries()) == 3
        assert history.get_latest().version == 3
        assert history.get_latest().description == "Third"
        
    def test_get_entry(self):
        """Test getting specific entry by version."""
        history = CostEstimateHistory()
        items1 = [{'name': 'Item 1', 'total_gross': 100.0}]
        items2 = [{'name': 'Item 2', 'total_gross': 200.0}]
        
        history.add_entry("First", items1)
        history.add_entry("Second", items2)
        
        entry = history.get_entry(1)
        assert entry is not None
        assert entry.version == 1
        assert entry.description == "First"
        
        entry = history.get_entry(2)
        assert entry is not None
        assert entry.version == 2
        
        entry = history.get_entry(999)
        assert entry is None
        
    def test_max_history_entries(self):
        """Test that history is limited to MAX_HISTORY_ENTRIES."""
        history = CostEstimateHistory()
        max_entries = CostEstimateHistory.MAX_HISTORY_ENTRIES
        
        # Add more than max entries
        for i in range(max_entries + 10):
            items = [{'name': f'Item {i}', 'total_gross': float(i)}]
            history.add_entry(f"Version {i}", items)
        
        # Should only keep max entries
        assert len(history.get_all_entries()) == max_entries
        
        # Latest should be the last one added
        latest = history.get_latest()
        assert latest.description == f"Version {max_entries + 9}"
        
    def test_calculate_checksum(self):
        """Test checksum calculation."""
        items1 = [{'name': 'Item 1', 'quantity': 10}]
        items2 = [{'name': 'Item 1', 'quantity': 10}]
        items3 = [{'name': 'Item 1', 'quantity': 20}]
        
        checksum1 = CostEstimateHistory.calculate_checksum(items1)
        checksum2 = CostEstimateHistory.calculate_checksum(items2)
        checksum3 = CostEstimateHistory.calculate_checksum(items3)
        
        # Same items should have same checksum
        assert checksum1 == checksum2
        
        # Different items should have different checksum
        assert checksum1 != checksum3
        
    def test_compare_versions(self):
        """Test comparing two versions."""
        history = CostEstimateHistory()
        
        items1 = [
            {'name': 'Item A', 'unit': 'm', 'quantity': 10, 'price_unit_net': 5.0},
            {'name': 'Item B', 'unit': 'szt', 'quantity': 5, 'price_unit_net': 10.0}
        ]
        
        items2 = [
            {'name': 'Item A', 'unit': 'm', 'quantity': 15, 'price_unit_net': 5.0},  # Changed quantity
            {'name': 'Item C', 'unit': 'kg', 'quantity': 20, 'price_unit_net': 3.0}  # New item
            # Item B removed
        ]
        
        history.add_entry("Version 1", items1)
        history.add_entry("Version 2", items2)
        
        comparison = history.compare_versions(1, 2)
        
        # Check added items
        assert len(comparison['added']) == 1
        assert comparison['added'][0]['name'] == 'Item C'
        
        # Check removed items
        assert len(comparison['removed']) == 1
        assert comparison['removed'][0]['name'] == 'Item B'
        
        # Check changed items
        assert len(comparison['changed']) == 1
        assert comparison['changed'][0]['old']['name'] == 'Item A'
        assert comparison['changed'][0]['new']['quantity'] == 15
        
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        history = CostEstimateHistory()
        items1 = [{'name': 'Item 1', 'total_gross': 100.0}]
        items2 = [{'name': 'Item 2', 'total_gross': 200.0}]
        
        history.add_entry("First", items1)
        history.add_entry("Second", items2)
        
        # Convert to dict
        data = history.to_dict()
        assert data['current_version'] == 2
        assert len(data['entries']) == 2
        
        # Create new history from dict
        new_history = CostEstimateHistory.from_dict(data)
        assert len(new_history.get_all_entries()) == 2
        assert new_history.get_latest().description == "Second"
        
    def test_clear_history(self):
        """Test clearing all history entries."""
        history = CostEstimateHistory()
        items = [{'name': 'Item 1', 'total_gross': 100.0}]
        
        history.add_entry("First", items)
        history.add_entry("Second", items)
        
        assert len(history.get_all_entries()) == 2
        
        history.clear()
        
        assert len(history.get_all_entries()) == 0
        assert history.get_latest() is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
