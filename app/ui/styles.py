"""
UI Styles and theme configuration for the Ofertownik application.
Provides modern color palette and ttk styling with dark mode support.
"""

from tkinter import ttk
from typing import Dict, Callable, Optional
import tkinter as tk


# Modern color palette for roofing application
COLORS: Dict[str, str] = {
    'primary': '#2C3E50',        # Dark blue-gray for headers
    'secondary': '#34495E',      # Lighter blue-gray
    'accent': '#F1C40F',         # Sunny yellow accent (was orange)
    'accent_dark': '#D4AC0D',    # Darker yellow (was darker orange)
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
    'table_header': '#F9E79F',   # Light yellow table header (was warm orange)
    'table_alt': '#FEFCF3',      # Very light yellow alternate row (was light orange)
    'table_header': '#F9E79F',   # Table header (warm yellow)
    'table_alt': '#FEFCF3',      # Alternate row color
}

# Dark mode color palette
COLORS_DARK: Dict[str, str] = {
    'primary': '#1A252F',        # Very dark blue-gray
    'secondary': '#2C3E50',      # Dark blue-gray
    'accent': '#F1C40F',         # Sunny yellow accent (was orange)
    'accent_dark': '#D4AC0D',    # Darker yellow (was darker orange)
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
    'table_header': '#5D4E37',   # Dark yellow table header (was dark brown)
    'table_alt': '#3D3D3D',      # Dark alternate row
}


class ThemeManager:
    """
    Manages application theme switching between light and dark modes.
    """
    
    _instance: Optional['ThemeManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._dark_mode = False
        self._root: Optional[tk.Tk] = None
        self._style: Optional[ttk.Style] = None
        self._callbacks: list[Callable[[bool], None]] = []
    
    @property
    def dark_mode(self) -> bool:
        """Returns True if dark mode is enabled."""
        return self._dark_mode
    
    @property
    def colors(self) -> Dict[str, str]:
        """Returns the current color palette based on theme."""
        return COLORS_DARK if self._dark_mode else COLORS
    
    def initialize(self, root: tk.Tk, dark_mode: bool = False) -> ttk.Style:
        """
        Initialize the theme manager with the root window.
        
        Args:
            root: The root Tk window
            dark_mode: Initial dark mode state
            
        Returns:
            The configured ttk.Style object
        """
        self._root = root
        self._dark_mode = dark_mode
        self._style = apply_modern_style(root, dark_mode)
        return self._style
    
    def toggle_theme(self) -> bool:
        """
        Toggle between light and dark mode.
        
        Returns:
            The new dark mode state
        """
        self._dark_mode = not self._dark_mode
        if self._root:
            self._style = apply_modern_style(self._root, self._dark_mode)
            self._root.configure(bg=self.colors['bg_light'])
            # Notify all registered callbacks
            for callback in self._callbacks:
                try:
                    callback(self._dark_mode)
                except Exception:
                    pass
        return self._dark_mode
    
    def set_theme(self, dark_mode: bool) -> None:
        """
        Set the theme explicitly.
        
        Args:
            dark_mode: True for dark mode, False for light mode
        """
        if self._dark_mode != dark_mode:
            self.toggle_theme()
    
    def register_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Register a callback to be called when theme changes.
        
        Args:
            callback: Function that takes a bool (dark_mode state)
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Unregister a previously registered callback.
        
        Args:
            callback: The callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# Global theme manager instance
theme_manager = ThemeManager()


def get_colors(dark_mode: bool = False) -> Dict[str, str]:
    """
    Get the color palette for the specified mode.
    
    Args:
        dark_mode: Whether to return dark mode colors
        
    Returns:
        Dictionary of color values
    """
    return COLORS_DARK if dark_mode else COLORS


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
                   foreground=colors['primary'] if not dark_mode else colors['accent'], 
                   font=('Segoe UI', 11, 'bold'))
    
    # Configure buttons
    style.configure('TButton', 
                    background=colors['primary'], 
                    foreground=colors['text_dark'] if dark_mode else colors['bg_white'],
                    padding=(10, 5),
                    font=('Segoe UI', 10))
    style.map('TButton', 
              background=[('active', colors['secondary']), 
                         ('pressed', colors['accent_dark'])])
    
    # Accent button style
    style.configure('Accent.TButton', 
                    background=colors['accent'],
                    foreground=colors['primary'],
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
    
    # Danger button style (for dark mode toggle visibility)
    style.configure('Danger.TButton', 
                    background=colors['danger'],
                    foreground=colors['bg_white'],
                    padding=(10, 5),
                    font=('Segoe UI', 10))
    style.map('Danger.TButton', 
              background=[('active', '#C0392B')])
    
    # Theme toggle button style
    style.configure('Theme.TButton',
                    background=colors['secondary'],
                    foreground=colors['bg_white'] if not dark_mode else colors['text_dark'],
                    padding=(8, 4),
                    font=('Segoe UI', 9))
    style.map('Theme.TButton',
              background=[('active', colors['primary'])])
    
    # Configure entries
    style.configure('TEntry', 
                    fieldbackground=colors['bg_white'],
                    foreground=colors['text_dark'],
                    insertcolor=colors['text_dark'],
                    borderwidth=2,
                    relief='flat')
    
    # Configure comboboxes
    style.configure('TCombobox', 
                    fieldbackground=colors['bg_white'],
                    background=colors['bg_white'],
                    foreground=colors['text_dark'],
                    arrowcolor=colors['text_dark'])
    style.map('TCombobox',
              fieldbackground=[('readonly', colors['bg_white'])],
              foreground=[('readonly', colors['text_dark'])])
    
    # Configure spinbox
    style.configure('TSpinbox',
                    fieldbackground=colors['bg_white'],
                    foreground=colors['text_dark'],
                    arrowcolor=colors['text_dark'])
    
    # Configure checkbuttons
    style.configure('TCheckbutton',
                    background=colors['bg_light'],
                    foreground=colors['text_dark'],
                    font=('Segoe UI', 10))
    style.map('TCheckbutton',
              background=[('active', colors['bg_light'])])
    
    # Configure radiobuttons
    style.configure('TRadiobutton',
                    background=colors['bg_light'],
                    foreground=colors['text_dark'],
                    font=('Segoe UI', 10))
    style.map('TRadiobutton',
              background=[('active', colors['bg_light'])])
    
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
              foreground=[('selected', colors['primary']), 
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
              foreground=[('selected', colors['primary'])])
    
    # Configure Panedwindow
    style.configure('TPanedwindow', background=colors['bg_light'])
    
    # Configure Separator
    style.configure('TSeparator', background=colors['border'])
    
    # Configure Scrollbar
    style.configure('TScrollbar',
                    background=colors['bg_light'],
                    troughcolor=colors['bg_white'],
                    arrowcolor=colors['text_dark'])
    
    # Configure Scale
    style.configure('TScale',
                    background=colors['bg_light'],
                    troughcolor=colors['bg_white'])
    
    # Configure Progressbar
    style.configure('TProgressbar',
                    background=colors['accent'],
                    troughcolor=colors['bg_white'])
    
    # Configure Text widget colors (for tk.Text, not ttk)
    # These will be applied separately to Text widgets
    
    return style


def configure_text_widget(widget: tk.Text, dark_mode: bool = False) -> None:
    """
    Configure a tk.Text widget with theme colors.
    
    Args:
        widget: The Text widget to configure
        dark_mode: Whether to use dark mode colors
    """
    colors = COLORS_DARK if dark_mode else COLORS
    widget.configure(
        bg=colors['bg_white'],
        fg=colors['text_dark'],
        insertbackground=colors['text_dark'],
        selectbackground=colors['accent'],
        selectforeground=colors['primary']
    )


def configure_listbox(widget: tk.Listbox, dark_mode: bool = False) -> None:
    """
    Configure a tk.Listbox widget with theme colors.
    
    Args:
        widget: The Listbox widget to configure
        dark_mode: Whether to use dark mode colors
    """
    colors = COLORS_DARK if dark_mode else COLORS
    widget.configure(
        bg=colors['bg_white'],
        fg=colors['text_dark'],
        selectbackground=colors['accent'],
        selectforeground=colors['primary']
    )


def configure_canvas(widget: tk.Canvas, dark_mode: bool = False) -> None:
    """
    Configure a tk.Canvas widget with theme colors.
    
    Args:
        widget: The Canvas widget to configure
        dark_mode: Whether to use dark mode colors
    """
    colors = COLORS_DARK if dark_mode else COLORS
    widget.configure(bg=colors['bg_white'])
