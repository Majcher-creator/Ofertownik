# Quick Start Guide - Ofertownik v4.7.0

## For Users

### Installation
```bash
# Clone repository
git clone https://github.com/Majcher-creator/Ofertownik.git
cd Ofertownik

# Install dependencies
pip install -r requirements.txt

# Run application
python main_app044.py
```

### First Run
1. Application opens with modern UI
2. Create your first cost estimate in the "Kosztorys/Oferta" tab
3. Use calculators in other tabs (Pomiar, Rynny, Kominy, Obróbki)
4. Export to PDF or CSV when done

## For Developers

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_validation.py -v
```

### Using New Modules

#### Database
```python
from app.services.database import Database

db = Database()
client_id = db.create_client(name="Test Client", tax_id="5260250274")
```

#### Validation
```python
from app.utils.validation import validate_nip, validate_cost_item

# Validate NIP
if validate_nip("5260250274"):
    print("Valid NIP!")

# Validate cost item
is_valid, error = validate_cost_item(item_dict)
```

#### CSV Export
```python
from app.services.csv_export import CSVExporter

CSVExporter.export_items_to_csv(items, "output.csv")
```

### Project Structure
```
app/
├── models/      # Data models
├── services/    # Business logic (DB, files, exports)
├── ui/          # UI components (styles, dialogs)
└── utils/       # Utilities (formatting, validation)

tests/          # Unit tests (49 tests)
```

### Key Files
- `README.md` - Full documentation
- `REFACTORING_SUMMARY.md` - What changed
- `IMPLEMENTATION_NOTES.md` - Technical details
- `requirements.txt` - Dependencies
- `.env.example` - Configuration template

### Making Changes
1. Create feature branch from this branch
2. Add tests for new functionality
3. Run `pytest` to verify
4. Update documentation
5. Create PR

## Common Tasks

### Add a New Validation Rule
1. Edit `app/utils/validation.py`
2. Add function with type hints
3. Add test in `tests/test_validation.py`
4. Run `pytest tests/test_validation.py`

### Add Database Table
1. Edit `app/services/database.py`
2. Add table in `_create_tables()`
3. Add CRUD methods
4. Add migration if needed

### Export to New Format
1. Create `app/services/xyz_export.py`
2. Implement export function
3. Add to main app menu/buttons

## Help & Resources

- **Issues**: https://github.com/Majcher-creator/Ofertownik/issues
- **Documentation**: See README.md
- **Tests**: See tests/ directory for examples

## Quick Reference

### Test Count: 49
- Roof calculations: 10
- Gutter calculations: 11  
- Cost calculations: 9
- Validation: 19

### Python Version: 3.10+

### Dependencies:
- reportlab (PDF)
- Pillow (images)
- pytest (testing)

All tests passing ✅
