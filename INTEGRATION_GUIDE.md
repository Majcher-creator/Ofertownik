# Integration Guide - Modular Structure

## Overview

This guide explains how the Ofertownik application integrates with the new modular structure in the `app/` directory. The integration maintains full backward compatibility while providing a cleaner, more maintainable architecture.

## Architecture

### Modular Structure

```
app/
├── __init__.py              # Package exports
├── models/                  # Data models
│   ├── client.py           # Client dataclass
│   ├── cost_item.py        # CostItem dataclass
│   └── material.py         # Material dataclass
├── services/               # Business logic layer
│   ├── database.py         # SQLite database manager
│   ├── file_manager.py     # JSON file operations
│   └── csv_export.py       # CSV export functionality
├── ui/                     # User interface components
│   ├── styles.py           # Theme and styling
│   ├── dialogs.py          # Dialog windows
│   └── tabs/               # Tab components (future)
└── utils/                  # Utility functions
    ├── formatting.py       # Number and string formatting
    └── validation.py       # Data validation
```

## Using the Modular Structure

### Importing Core Components

```python
# Import from top-level package
from app import Client, CostItem, Material
from app import Database, FileManager
from app import fmt_money, validate_nip

# Or import from specific modules
from app.models import Client, CostItem
from app.services import Database
from app.utils.formatting import fmt_money
from app.utils.validation import validate_cost_item
```

### Using Data Models

#### Client Model

```python
from app.models import Client

# Create a new client
client = Client(
    name="Firma ABC",
    address="ul. Testowa 1, Warszawa",
    id="123-456-78-90",  # NIP
    phone="123-456-789",
    email="kontakt@firma.pl"
)

# Convert to dict (for JSON serialization)
client_dict = client.to_dict()

# Load from dict
client = Client.from_dict(client_dict)

# Validate
if client.is_valid():
    print(f"Client {client.name} is valid")
```

#### CostItem Model

```python
from app.models import CostItem

# Create a cost item
item = CostItem(
    name="Blacha dachowa",
    quantity=100.0,
    unit="m²",
    price_unit_net=45.50,
    vat_rate=23,
    category="material",
    note="Kolor grafitowy"
)

# Calculate totals
item.calculate_totals()
print(f"Total net: {item.total_net} zł")
print(f"VAT: {item.vat_value} zł")
print(f"Total gross: {item.total_gross} zł")

# Convert to/from dict
item_dict = item.to_dict()
loaded_item = CostItem.from_dict(item_dict)
```

#### Material Model

```python
from app.models import Material

# Create a material
material = Material(
    name="Blacha trapezowa T-35",
    unit="m²",
    price_net=42.00,
    vat_rate=23,
    category="material",
    description="Powłoka poliestrowa, gr. 0.5mm"
)

# Convert to dict
mat_dict = material.to_dict()
```

### Using Services

#### Database Service

```python
from app.services import Database

# Initialize database
db = Database("ofertownik.db")

# Create a client
client_id = db.create_client(
    name="Jan Kowalski",
    address="ul. Główna 10, Kraków",
    tax_id="123-456-78-90",
    phone="600-123-456",
    email="jan@example.com"
)

# Get client by ID
client = db.get_client(client_id)
print(client['name'])

# List all clients
clients = db.list_clients()
for c in clients:
    print(f"{c['name']} - {c['tax_id']}")

# Update client
db.update_client(client_id, name="Jan Kowalski - Updated")

# Delete client
db.delete_client(client_id)

# Settings management
db.set_setting('last_invoice_number', '2024-001')
invoice_num = db.get_setting('last_invoice_number')

# Create backup
backup_path = db.create_backup()
print(f"Backup created: {backup_path}")
```

#### File Manager Service

```python
from app.services import FileManager

# Load JSON file
data = FileManager.load_json('settings.json')

# Save JSON file
FileManager.save_json('settings.json', {'key': 'value'})

# Load materials database
materials = FileManager.load_materials_database('materialy_uslugi.json')

# Save materials database
FileManager.save_materials_database(materials, 'materialy_uslugi.json')

# Load cost estimate
estimate = FileManager.load_cost_estimate('estimate.cost.json')

# Save cost estimate
FileManager.save_cost_estimate(estimate_data, 'estimate.cost.json')

# Load settings
settings = FileManager.load_settings()

# Save settings
FileManager.save_settings(settings)
```

#### CSV Exporter Service

```python
from app.services.csv_export import CSVExporter

# Create exporter
exporter = CSVExporter()

# Export cost items to CSV
cost_items = [
    {"name": "Item 1", "quantity": 10, "unit": "szt", "price_unit_net": 50.0},
    {"name": "Item 2", "quantity": 5, "unit": "m²", "price_unit_net": 100.0}
]

exporter.export_cost_items(cost_items, "output.csv")
```

### Using Utilities

#### Formatting Functions

```python
from app.utils.formatting import fmt_money, fmt_money_plain, safe_filename

# Format money values
print(fmt_money(1234.56))        # "1 234,56 zł"
print(fmt_money_plain(1234.56))  # "1 234,56"

# Create safe filenames
filename = safe_filename("Kosztorys 2024/01")  # "Kosztorys_202401"
```

#### Validation Functions

```python
from app.utils.validation import (
    validate_cost_item,
    validate_client,
    validate_nip,
    validate_positive_number,
    validate_dimensions
)

# Validate cost item
item = {"name": "Test", "quantity": 10, "price_unit_net": 50.0}
is_valid, error_msg = validate_cost_item(item)
if not is_valid:
    print(f"Validation error: {error_msg}")

# Validate client
client = {"name": "Test Client", "email": "test@example.com"}
is_valid, error_msg = validate_client(client)

# Validate NIP (Polish tax ID with checksum)
if validate_nip("526-025-02-74"):
    print("Valid NIP")

# Validate positive number
is_valid, error_msg = validate_positive_number(100.5, "Price")

# Validate dimensions
is_valid, error_msg = validate_dimensions(10.0, 8.0)
```

### Using UI Components

#### Dialog Classes

```python
from app.ui.dialogs import ClientDialog, CostItemEditDialog, MaterialEditDialog

# Note: These require tkinter and must be used within a tkinter application

# Client dialog
dialog = ClientDialog(parent, "Add Client", client=None)
if dialog.result:
    client_data = dialog.result
    print(f"Client: {client_data['name']}")

# Cost item dialog
dialog = CostItemEditDialog(parent, "Edit Item", item=existing_item)
if dialog.result:
    updated_item = dialog.result
    
# Material dialog
dialog = MaterialEditDialog(parent, "Add Material", material=None)
if dialog.result:
    material_data = dialog.result
```

## Integration in main_app044.py

The main application file (`main_app044.py`) now imports utilities and dialogs from the `app/` package:

```python
# Import app modules (new modular structure from app/)
try:
    from app.utils.formatting import fmt_money, fmt_money_plain, is_valid_float_text
    from app.ui.dialogs import ClientDialog, CostItemEditDialog, MaterialEditDialog
    APP_MODULES_AVAILABLE = True
except ImportError:
    APP_MODULES_AVAILABLE = False
    # Fallback implementations provided for backward compatibility
```

This approach:
- ✅ Uses modular structure when available
- ✅ Provides fallback for backward compatibility
- ✅ Maintains full functionality
- ✅ Enables gradual migration

## Migration Strategy

### Current State (v4.7)

- ✅ Core models created (Client, CostItem, Material)
- ✅ Services implemented (Database, FileManager, CSVExporter)
- ✅ Utilities available (formatting, validation)
- ✅ Dialogs extracted to app/ui/dialogs.py
- ✅ main_app044.py imports utilities and dialogs
- ✅ Full backward compatibility maintained
- ✅ All 49 tests passing

### Next Steps (Future)

1. **Extract tab components** to `app/ui/tabs/`:
   - `cost_tab.py` - Main cost estimate tab
   - `measurement_tab.py` - Roof measurement tab
   - `gutter_tab.py` - Gutter calculation tab
   - `chimney_tab.py` - Chimney calculation tab
   - `flashing_tab.py` - Flashing calculation tab

2. **Create main app wrapper** in `app/main.py`:
   - Import tab components
   - Use modular structure throughout
   - Maintain backward compatibility

3. **Update main_app044.py** to use tab components:
   - Import tabs from `app/ui/tabs/`
   - Reduce duplication
   - Target < 500 lines

4. **Convert data structures**:
   - Use `Client` dataclass instead of dicts
   - Use `CostItem` dataclass for items
   - Use `Material` dataclass for materials

5. **Use services**:
   - Integrate `Database` for data persistence
   - Use `FileManager` for all file operations
   - Use `CSVExporter` for exports

## Benefits

### For Developers

- **Clearer structure**: Code organized by responsibility
- **Easier testing**: Modular components can be tested independently
- **Better IDE support**: Type hints and clear interfaces
- **Easier maintenance**: Find and fix bugs in specific modules

### For Users

- **More reliable**: Comprehensive testing ensures quality
- **Better validation**: Robust data validation (including NIP checksum)
- **Future features**: Foundation for database-backed storage
- **Backward compatible**: Existing .cost.json files work without changes

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_validation.py -v
```

All 49 tests should pass:
- 9 cost calculation tests
- 11 gutter calculation tests  
- 10 roof calculation tests
- 19 validation tests

## Backward Compatibility

The integration maintains 100% backward compatibility:

- ✅ Existing `.cost.json` files load correctly
- ✅ `main_app044.py` runs independently
- ✅ All calculation modules work unchanged
- ✅ Fallback implementations provided
- ✅ No breaking changes to APIs

## Conclusion

The modular structure is now integrated into the Ofertownik application, providing a solid foundation for future development while maintaining full backward compatibility. Developers can gradually adopt the new structure, using utilities, models, and services as needed.
