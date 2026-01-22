"""Tests for dark mode and theme switching."""
import pytest
from app.ui.styles import COLORS, COLORS_DARK, get_colors, ThemeManager


def test_colors_have_all_keys():
    """Test that both color palettes have the same keys."""
    assert set(COLORS.keys()) == set(COLORS_DARK.keys())


def test_get_colors_light():
    """Test get_colors returns light colors by default."""
    colors = get_colors(dark_mode=False)
    assert colors == COLORS


def test_get_colors_dark():
    """Test get_colors returns dark colors when dark_mode=True."""
    colors = get_colors(dark_mode=True)
    assert colors == COLORS_DARK


def test_theme_manager_singleton():
    """Test ThemeManager is a singleton."""
    tm1 = ThemeManager()
    tm2 = ThemeManager()
    assert tm1 is tm2


def test_theme_manager_default_light():
    """Test ThemeManager defaults to light mode."""
    tm = ThemeManager()
    # Reset for testing
    tm._dark_mode = False
    assert tm.dark_mode == False
    assert tm.colors == COLORS


def test_theme_manager_dark_mode():
    """Test ThemeManager can switch to dark mode."""
    tm = ThemeManager()
    # Set dark mode
    tm._dark_mode = True
    assert tm.dark_mode == True
    assert tm.colors == COLORS_DARK


def test_colors_structure():
    """Test that color dictionaries have expected keys."""
    required_keys = [
        'primary', 'secondary', 'accent', 'accent_dark',
        'success', 'warning', 'danger',
        'bg_light', 'bg_white',
        'text_dark', 'text_light',
        'border', 'table_header', 'table_alt'
    ]
    
    for key in required_keys:
        assert key in COLORS, f"Missing key {key} in COLORS"
        assert key in COLORS_DARK, f"Missing key {key} in COLORS_DARK"


def test_colors_are_strings():
    """Test that all color values are strings (hex codes)."""
    for key, value in COLORS.items():
        assert isinstance(value, str), f"COLORS[{key}] is not a string"
        assert value.startswith('#'), f"COLORS[{key}] is not a hex color"
    
    for key, value in COLORS_DARK.items():
        assert isinstance(value, str), f"COLORS_DARK[{key}] is not a string"
        assert value.startswith('#'), f"COLORS_DARK[{key}] is not a hex color"
