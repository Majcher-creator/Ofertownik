# Keyboard Shortcuts and Multi-Select Feature

## Summary

This update adds comprehensive keyboard shortcuts and multi-select functionality to the Ofertownik cost estimation application, significantly improving user productivity and workflow efficiency.

## Changes Made

### 1. Global Keyboard Shortcuts

Added keyboard shortcuts for main application functions:

| Shortcut | Action | Menu |
|----------|--------|------|
| `Ctrl+N` | New cost estimate | File |
| `Ctrl+S` | Save cost estimate | File |
| `Ctrl+O` | Load cost estimate | File |
| `Ctrl+P` | Export to PDF | Export |
| `Ctrl+E` | Export to CSV | Export |
| `F5` | Calculate/Recalculate | Calculations |
| `Ctrl+Q` | Quit application | File |
| `F1` | Show help | Help |

**Cross-platform support**: The implementation automatically detects macOS and supports both `Control` and `Command` modifiers.

### 2. Multi-Select Support in Lists

Changed the Treeview `selectmode` from `"browse"` (single selection) to `"extended"` (multiple selection) for both:
- Materials tree (`self.mat_tree`)
- Services tree (`self.srv_tree`)

This allows users to:
- Select multiple items using Ctrl+Click
- Select ranges using Shift+Click
- Perform batch operations on multiple items

### 3. List Keyboard Shortcuts

Added keyboard shortcuts for list operations:

| Shortcut | Action |
|----------|--------|
| `Enter` | Edit selected item (single selection only) |
| `Delete` | Delete selected items (supports multiple) |
| `Ctrl+A` | Select all items in current list |
| `Ctrl+D` | Duplicate selected items |
| `Ctrl+↑` | Move selected items up |
| `Ctrl+↓` | Move selected items down |

### 4. Context Menu (Right-Click)

Added comprehensive context menus for both materials and services lists:

```
✏️ Edytuj (Edit)
📋 Duplikuj (Duplicate)
────────────────
⬆️ Przesuń w górę (Move up)
⬇️ Przesuń w dół (Move down)
────────────────
🔄 Zmień kategorię (Change category)
────────────────
🗑️ Usuń (Delete)
🗑️ Usuń wszystkie (Clear all)
```

### 5. New Methods

#### `setup_keyboard_shortcuts()`
Sets up all global keyboard shortcuts with cross-platform support.

#### `show_help()`
Displays a help dialog showing all available keyboard shortcuts.

#### `create_status_bar()`
Creates a status bar at the bottom of the window showing most common shortcuts.

#### `_setup_tree_bindings()`
Configures keyboard shortcuts and context menus for both tree views.

#### `create_context_menu(tree, kind)`
Creates a context menu for a specific tree view.

#### `show_context_menu(event, menu)`
Displays the context menu at the mouse position.

#### `_select_all(kind)`
Selects all items in the specified list (materials or services).

#### `_duplicate_items(kind)`
Duplicates the selected items in the list.

#### `_move_item_up(kind)`
Moves selected items up in the list, maintaining selection.

#### `_move_item_down(kind)`
Moves selected items down in the list, maintaining selection.

#### `_change_category(kind)`
Changes the category of selected items (material ↔ service).

#### `_clear_all(kind)`
Removes all items from the specified category (with confirmation).

### 6. Updated Methods

#### `_edit_from_tree(kind)`
- Now checks for multiple selections
- Shows a warning if more than one item is selected
- Only allows editing single items

#### `_delete_from_tree(kind)`
- Now supports deleting multiple items at once
- Shows count of items to be deleted in confirmation dialog
- Properly handles index shifts by deleting in reverse order

### 7. Enhanced Menu Bar

Added new menu sections and accelerator labels:

**Export Menu** (new):
- Export PDF (Ctrl+P)
- Export CSV (Ctrl+E)

**Calculations Menu** (new):
- Calculate estimate (F5)

**Help Menu** (new):
- About/Help (F1)

All existing menu items now show their keyboard shortcuts.

### 8. Status Bar

Added a status bar at the bottom of the window showing the most commonly used shortcuts:
```
Ctrl+S: Zapisz | Ctrl+O: Otwórz | F5: Oblicz | Del: Usuń | Enter: Edytuj | Ctrl+A: Zaznacz wszystkie | F1: Pomoc
```

## Technical Implementation Details

### Event Binding
- All keyboard shortcuts use lambda functions with proper event parameter handling
- Context menus use `tk.Menu` with `tearoff=0` for modern appearance
- Tree bindings capture the `kind` parameter using default arguments in lambda

### Multi-Select Logic
- Delete operations sort indices in reverse to avoid index shift issues
- Move operations maintain selection after moving
- Duplicate operations append to the end of the list

### Cross-Platform Compatibility
- Detects macOS using `platform.system() == 'Darwin'`
- Supports both Control and Command modifiers on macOS
- Uses platform-appropriate key names in help text

## User Benefits

1. **Faster Workflow**: Common operations accessible via keyboard shortcuts
2. **Batch Operations**: Select and modify multiple items at once
3. **Better UX**: Context menus provide quick access to operations
4. **Discoverability**: Menu accelerators and status bar show available shortcuts
5. **Help System**: F1 provides quick reference to all shortcuts

## Testing

All logic for the new features has been tested:
- ✓ Delete multiple items
- ✓ Duplicate items
- ✓ Move items up/down
- ✓ Change category
- ✓ Clear all in category

All existing tests (49 tests) continue to pass, confirming backward compatibility.

## Files Modified

- `main_app044.py`: All changes implemented in the main application file

## Backward Compatibility

All changes are fully backward compatible:
- Single-click selection still works as before
- Existing functionality unchanged
- Additional features only enhance user experience
- No changes to file formats or data structures

## Future Enhancements

Potential improvements for future versions:
- Undo/Redo functionality (Ctrl+Z, Ctrl+Y)
- Find/Search in lists (Ctrl+F)
- Keyboard navigation between tabs
- Copy/Paste between lists (Ctrl+C, Ctrl+V)
- Export preview (Ctrl+Shift+P)
