# PDF Preview Feature - Implementation Documentation

## Overview
This document describes the implementation of the PDF preview feature for the Ofertownik application.

## Features Added

### 1. PDF Preview Service (`app/services/pdf_preview.py`)
A new service class `PDFPreview` that provides:
- `preview_pdf()`: Generates a PDF to a temporary file and opens it in the default system application
- `open_file()`: Opens a file in the default application (cross-platform: Windows, macOS, Linux)
- `cleanup_temp_file()`: Removes temporary files after use

### 2. UI Enhancement
Added a new button "👁️ Podgląd PDF" to the cost estimation toolbar in `main_app044.py`:

```
┌─────────────────────────────────────────────────────────────────┐
│ Toolbar (zakładka Kosztorys)                                    │
├─────────────────────────────────────────────────────────────────┤
│ [📊 Oblicz kosztorys] [📄 Eksportuj CSV] [👁️ Podgląd PDF]     │
│ [📑 Eksportuj PDF]            [📦 Wstaw z bazy] [👥 Klienci]  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. User Workflow

#### Preview Workflow:
1. User clicks "👁️ Podgląd PDF" button
2. PDF is generated to a temporary file (e.g., `/tmp/ofertownik_preview_XXXXX.pdf`)
3. PDF opens in the default system application (Adobe Reader, browser, Preview on macOS, etc.)
4. After viewing, user closes the PDF viewer
5. Dialog appears: "Czy chcesz zapisać ten kosztorys do pliku?"
   - **Tak (Yes)**: File save dialog opens, user chooses location
   - **Nie (No)**: Temporary file is deleted, no save
6. Temporary file is cleaned up

#### Traditional Export Workflow (unchanged):
1. User clicks "📑 Eksportuj PDF" button
2. File save dialog opens immediately
3. PDF is generated and saved to chosen location
4. If "Open PDF after export" is checked, PDF opens automatically

## Technical Implementation

### Code Refactoring
To avoid code duplication, the PDF generation logic was extracted into a helper method:
- `_generate_pdf_to_path(path)`: Generates the PDF document to a specified path

This method is used by both:
- `export_cost_pdf()`: Direct export with save dialog
- `preview_cost_pdf()`: Preview with optional save

### Cross-Platform Support
The `PDFPreview.open_file()` method handles opening PDFs on different operating systems:

- **Windows**: Uses `os.startfile(path)`
- **macOS**: Uses `subprocess.Popen(['open', path])`
- **Linux**: Uses `subprocess.Popen(['xdg-open', path])`

### Temporary File Management
- Temporary files are created in the system temp directory
- Files are named with prefix `ofertownik_preview_` for easy identification
- Files have `.pdf` extension to ensure correct application association
- Cleanup happens automatically after the preview workflow completes

## Testing

### Unit Tests
Created comprehensive unit tests in `tests/test_pdf_preview.py`:
- 12 tests covering all functionality
- Mock-based testing for cross-platform compatibility
- Tests for error handling and edge cases

### Test Coverage
- ✅ Temporary file creation
- ✅ PDF generator invocation
- ✅ File opening on Windows/macOS/Linux
- ✅ Cleanup on success and failure
- ✅ Error handling for missing files
- ✅ Null/None parameter handling

All 61 tests pass (49 existing + 12 new).

## Benefits

1. **Better User Experience**: Users can review the PDF before saving
2. **Reduced Errors**: Catch formatting issues before final save
3. **Flexible Workflow**: Users can preview multiple times, adjusting data as needed
4. **No Clutter**: Temporary files are automatically cleaned up
5. **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

## Files Modified/Created

### Created:
- `app/services/pdf_preview.py` - PDF preview service
- `tests/test_pdf_preview.py` - Unit tests

### Modified:
- `main_app044.py` - Added preview button and workflow
- `app/services/__init__.py` - Exported PDFPreview class
- `README.md` - Documented new feature

## Future Enhancements (Optional)

1. **Auto-cleanup on exit**: Use `atexit` to clean up any orphaned temp files
2. **Preview history**: Keep last N previews until app closes
3. **Preview settings**: Allow user to choose preview behavior (always ask, always save, etc.)
4. **Preview annotations**: Allow users to add notes/comments during preview
