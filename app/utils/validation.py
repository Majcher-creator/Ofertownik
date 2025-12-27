"""
Validation utilities for the Ofertownik application.
Provides comprehensive validation for user inputs and data integrity.
"""

from typing import Tuple, Dict, Any
import re


def validate_cost_item(item: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a cost item dictionary.
    
    Args:
        item: Dictionary containing cost item data
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    if not item.get('name'):
        return False, "Nazwa jest wymagana"
    
    quantity = item.get('quantity', 0)
    try:
        quantity = float(quantity)
        if quantity < 0:
            return False, "Ilość nie może być ujemna"
    except (TypeError, ValueError):
        return False, "Ilość musi być liczbą"
    
    price = item.get('price_unit_net', 0)
    try:
        price = float(price)
        if price < 0:
            return False, "Cena nie może być ujemna"
    except (TypeError, ValueError):
        return False, "Cena musi być liczbą"
    
    vat_rate = item.get('vat_rate', 23)
    try:
        vat_rate = int(vat_rate)
        if vat_rate not in [0, 8, 23]:
            return False, "Stawka VAT musi być 0, 8 lub 23"
    except (TypeError, ValueError):
        return False, "Stawka VAT musi być liczbą całkowitą"
    
    return True, ""


def validate_client(client: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate client data dictionary.
    
    Args:
        client: Dictionary containing client data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not client.get('name'):
        return False, "Nazwa klienta jest wymagana"
    
    # Optional: validate email format if provided
    email = client.get('email', '').strip()
    if email:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Nieprawidłowy format adresu e-mail"
    
    # Optional: validate NIP if provided
    nip = client.get('id', '').strip()
    if nip and nip.replace('-', '').replace(' ', '').isdigit():
        if not validate_nip(nip):
            return False, "Nieprawidłowy numer NIP (błędna suma kontrolna)"
    
    return True, ""


def validate_nip(nip: str) -> bool:
    """
    Validate Polish NIP (Tax Identification Number) with checksum verification.
    
    Args:
        nip: NIP string (may contain dashes or spaces)
        
    Returns:
        True if NIP is valid, False otherwise
    """
    # Remove non-digit characters
    nip_clean = nip.replace('-', '').replace(' ', '')
    
    # NIP must have exactly 10 digits
    if len(nip_clean) != 10 or not nip_clean.isdigit():
        return False
    
    # Checksum calculation using weights
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    checksum = 0
    
    for i in range(9):
        checksum += int(nip_clean[i]) * weights[i]
    
    checksum = checksum % 11
    
    # If checksum is 10, NIP is invalid
    if checksum == 10:
        return False
    
    # Compare calculated checksum with the last digit
    return checksum == int(nip_clean[9])


def validate_positive_number(value: Any, field_name: str = "Wartość") -> Tuple[bool, str]:
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num = float(value)
        if num < 0:
            return False, f"{field_name} nie może być ujemna"
        return True, ""
    except (TypeError, ValueError):
        return False, f"{field_name} musi być liczbą"


def validate_dimensions(length: Any, width: Any) -> Tuple[bool, str]:
    """
    Validate roof dimensions.
    
    Args:
        length: Length value
        width: Width value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, msg = validate_positive_number(length, "Długość")
    if not is_valid:
        return False, msg
    
    is_valid, msg = validate_positive_number(width, "Szerokość")
    if not is_valid:
        return False, msg
    
    try:
        if float(length) == 0 or float(width) == 0:
            return False, "Wymiary nie mogą być równe zero"
    except (TypeError, ValueError):
        return False, "Wymiary muszą być liczbami"
    
    return True, ""
