"""
Formatting utilities for the Ofertownik application.
Provides functions for formatting monetary values and other display strings.
"""

from typing import Union
import re


def fmt_money_plain(value: float) -> str:
    """
    Format a float value as a plain money string with Polish formatting.
    
    Args:
        value: The monetary value to format
        
    Returns:
        Formatted string with space as thousands separator and comma as decimal separator
        Example: 1234.56 -> "1 234,56"
    """
    s = f"{value:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", " ")


def fmt_money(value: float) -> str:
    """
    Format a float value as money with 'zł' suffix.
    
    Args:
        value: The monetary value to format
        
    Returns:
        Formatted string with 'zł' suffix
        Example: 1234.56 -> "1 234,56 zł"
    """
    return fmt_money_plain(value) + " zł"


def is_valid_float_text(s: str) -> bool:
    """
    Validate if a string can be a valid float input during typing.
    Allows partial inputs like "-", ".", or incomplete numbers.
    
    Args:
        s: String to validate
        
    Returns:
        True if the string is a valid float or partial float input
    """
    if s == "" or s == "-" or s == ".":
        return True
    s = s.replace(",", ".")
    return bool(re.match(r'^\d+(\.\d{0,3})?$', s))


def safe_filename(s: str, maxlen: int = 140) -> str:
    """
    Convert a string to a safe filename by removing/replacing unsafe characters.
    
    Args:
        s: String to convert to safe filename
        maxlen: Maximum length of the resulting filename
        
    Returns:
        Safe filename string
    """
    s = s or ""
    s = s.strip()
    s = s.replace(" ", "_")
    s = re.sub(r'[^\w\-\._]', '', s)
    return s[:maxlen]
