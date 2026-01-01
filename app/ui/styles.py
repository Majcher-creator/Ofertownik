"""
UI Styles and theme configuration for the Ofertownik application.
Provides modern color palette and ttk styling.
"""

from tkinter import ttk
from typing import Dict


# Modern color palette for roofing application
COLORS: Dict[str, str] = {
    'primary': '#2C3E50',        # Dark blue-gray for headers
    'secondary': '#34495E',      # Lighter blue-gray
    'accent': '#F1C40F',         # Yellow accent
    'accent_dark': '#D4AC0D',    # Darker yellow
    'success': '#27AE60',        # Green for success
    'warning': '#F39C12',        # Yellow for warnings
    'danger': '#E74C3C',         # Red for errors
    'bg_light': '#ECF0F1',       # Light gray background
    'bg_white': '#FFFFFF',       # White
    'text_dark': '#2C3E50',      # Dark text
    'text_light': '#7F8C8D',     # Light gray text
    'border': '#BDC3C7',         # Border color
    'table_header': '#F9E79F',   # Table header (warm yellow)
    'table_alt': '#FEFCF3',      # Alternate row color
}

# Dark mode color palette
COLORS_DARK: Dict[str, str] = {
    'primary': '#1A252F',        # Very dark blue-gray
    'secondary': '#2C3E50',      # Dark blue-gray
    'accent': '#F1C40F',         # Yellow accent (same)
    'accent_dark': '#D4AC0D',    # Darker yellow (same)
    'success': '#27AE60',        # Green (same)
    'warning': '#F39C12',        # Yellow (same)
    'danger': '#E74C3C',         # Red (same)
    'bg_light': '#1E1E1E',       # Dark background
    'bg_white': '#2D2D30',       # Dark widget background
    'text_dark': '#E0E0E0',      # Light text for dark mode
    'text_light': '#9B9B9B',     # Gray text for dark mode
    'border': '#3E3E42',         # Dark border
    'table_header': '#3E2723',   # Dark table header
    'table_alt': '#252526',      # Dark alternate row
}


def apply_modern_style(root, dark_mode: bool = False) -> ttk.Style:
    """
    Apply modern styling to ttk widgets.
    
    Args:
        root: The root Tk window
        dark_mode: Whether to use dark mode colors
        
    Returns:
        The configured ttk.Style object
    """
    colors = COLORS_DARK if dark_mode else COLORS
    
    style = ttk.Style(root)
    style.theme_use('clam')  # Use clam theme as base
    
    # Configure general styles
    style.configure('TFrame', background=colors['bg_light'])
    style.configure('TLabel', 
                   background=colors['bg_light'], 
                   foreground=colors['text_dark'], 
                   font=('Segoe UI', 10))
    style.configure('TLabelframe', 
                   background=colors['bg_light'], 
                   foreground=colors['text_dark'])
    style.configure('TLabelframe.Label', 
                   background=colors['bg_light'], 
                   foreground=colors['primary'], 
                   font=('Segoe UI', 11, 'bold'))
    
    # Configure buttons
    style.configure('TButton', 
                    background=colors['primary'], 
                    foreground=colors['bg_white'],
                    padding=(10, 5),
                    font=('Segoe UI', 10))
    style.map('TButton', 
              background=[('active', colors['secondary']), 
                         ('pressed', colors['accent_dark'])])
    
    # Accent button style
    style.configure('Accent.TButton', 
                    background=colors['accent'],
                    foreground=colors['bg_white'],
                    padding=(12, 6),
                    font=('Segoe UI', 10, 'bold'))
    style.map('Accent.TButton', 
              background=[('active', colors['accent_dark'])])
    
    # Success button style
    style.configure('Success.TButton', 
                    background=colors['success'],
                    foreground=colors['bg_white'],
                    padding=(10, 5),
                    font=('Segoe UI', 10))
    style.map('Success.TButton', 
              background=[('active', '#229954')])
    
    # Configure entries
    style.configure('TEntry', 
                    fieldbackground=colors['bg_white'],
                    borderwidth=2,
                    relief='flat')
    
    # Configure comboboxes
    style.configure('TCombobox', 
                    fieldbackground=colors['bg_white'],
                    background=colors['bg_white'])
    
    # Configure notebooks/tabs
    style.configure('TNotebook', background=colors['bg_light'])
    style.configure('TNotebook.Tab', 
                    background=colors['bg_light'],
                    foreground=colors['text_dark'],
                    padding=(15, 8),
                    font=('Segoe UI', 10))
    style.map('TNotebook.Tab',
              background=[('selected', colors['accent']), 
                         ('active', colors['secondary'])],
              foreground=[('selected', colors['bg_white']), 
                         ('active', colors['bg_white'])])
    
    # Configure Treeview
    style.configure('Treeview',
                    background=colors['bg_white'],
                    foreground=colors['text_dark'],
                    fieldbackground=colors['bg_white'],
                    rowheight=28,
                    font=('Segoe UI', 10))
    style.configure('Treeview.Heading',
                    background=colors['table_header'],
                    foreground=colors['text_dark'],
                    font=('Segoe UI', 10, 'bold'))
    style.map('Treeview',
              background=[('selected', colors['accent'])],
              foreground=[('selected', colors['bg_white'])])
    
    # Configure Panedwindow
    style.configure('TPanedwindow', background=colors['bg_light'])
    
    # Configure Separator
    style.configure('TSeparator', background=colors['border'])
    
    return style
