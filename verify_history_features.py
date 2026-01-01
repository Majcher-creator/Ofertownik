#!/usr/bin/env python3
"""
Manual verification script for cost estimate history and templates.
Demonstrates the new features without needing the full GUI.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.history import CostEstimateHistory
from datetime import datetime


def demo_history():
    """Demonstrate history functionality."""
    print("\n" + "="*60)
    print("DEMONSTRACJA HISTORII KOSZTORYSU")
    print("="*60)
    
    # Create history
    history = CostEstimateHistory()
    
    # Add some versions
    print("\n1. Dodawanie wersji do historii...")
    
    items_v1 = [
        {'name': 'Blachodachówka', 'quantity': 100, 'unit': 'm²', 'price_unit_net': 35.0, 'total_gross': 3500.0},
        {'name': 'Łaty drewniane', 'quantity': 150, 'unit': 'mb', 'price_unit_net': 4.5, 'total_gross': 675.0}
    ]
    
    items_v2 = [
        {'name': 'Blachodachówka', 'quantity': 120, 'unit': 'm²', 'price_unit_net': 35.0, 'total_gross': 4200.0},  # Zwiększona ilość
        {'name': 'Łaty drewniane', 'quantity': 150, 'unit': 'mb', 'price_unit_net': 4.5, 'total_gross': 675.0},
        {'name': 'Membrana', 'quantity': 110, 'unit': 'm²', 'price_unit_net': 2.8, 'total_gross': 308.0}  # Nowa pozycja
    ]
    
    items_v3 = [
        {'name': 'Blachodachówka', 'quantity': 120, 'unit': 'm²', 'price_unit_net': 38.0, 'total_gross': 4560.0},  # Zmieniona cena
        {'name': 'Łaty drewniane', 'quantity': 150, 'unit': 'mb', 'price_unit_net': 4.5, 'total_gross': 675.0},
        {'name': 'Membrana', 'quantity': 110, 'unit': 'm²', 'price_unit_net': 2.8, 'total_gross': 308.0}
    ]
    
    # Add versions
    entry1 = history.add_entry("Wersja początkowa", items_v1, {'client': 'Jan Kowalski'})
    print(f"   ✓ Wersja {entry1.version}: {entry1.description} - {entry1.items_count} pozycji, {entry1.total_gross:.2f} zł")
    
    entry2 = history.add_entry("Dodano membranę, zwiększono powierzchnię", items_v2, {'client': 'Jan Kowalski'})
    print(f"   ✓ Wersja {entry2.version}: {entry2.description} - {entry2.items_count} pozycji, {entry2.total_gross:.2f} zł")
    
    entry3 = history.add_entry("Zmieniono cenę blachodachówki", items_v3, {'client': 'Jan Kowalski'})
    print(f"   ✓ Wersja {entry3.version}: {entry3.description} - {entry3.items_count} pozycji, {entry3.total_gross:.2f} zł")
    
    # Show all versions
    print("\n2. Lista wszystkich wersji:")
    for entry in history.get_all_entries():
        print(f"   v{entry.version}: {entry.description}")
        print(f"      Data: {entry.timestamp.split('T')[0]}")
        print(f"      Pozycje: {entry.items_count}, Wartość: {entry.total_gross:.2f} zł")
        print(f"      Checksum: {entry.checksum[:16]}...")
    
    # Get specific version
    print("\n3. Pobieranie konkretnej wersji (v2):")
    v2 = history.get_entry(2)
    if v2:
        print(f"   Wersja: {v2.version}")
        print(f"   Opis: {v2.description}")
        print(f"   Pozycje:")
        for item in v2.items_snapshot:
            print(f"      - {item['name']}: {item['quantity']} {item['unit']}")
    
    # Compare versions
    print("\n4. Porównywanie wersji 1 i 2:")
    comparison = history.compare_versions(1, 2)
    
    print(f"   Dodane pozycje ({len(comparison['added'])}):")
    for item in comparison['added']:
        print(f"      + {item['name']}: {item['quantity']} {item['unit']}")
    
    print(f"   Usunięte pozycje ({len(comparison['removed'])}):")
    for item in comparison['removed']:
        print(f"      - {item['name']}: {item['quantity']} {item['unit']}")
    
    print(f"   Zmienione pozycje ({len(comparison['changed'])}):")
    for change in comparison['changed']:
        print(f"      ~ {change['old']['name']}")
        print(f"        Ilość: {change['old']['quantity']} → {change['new']['quantity']}")
    
    # Serialize and deserialize
    print("\n5. Serializacja historii:")
    data = history.to_dict()
    print(f"   ✓ Wyeksportowano {len(data['entries'])} wersji")
    
    new_history = CostEstimateHistory.from_dict(data)
    print(f"   ✓ Zaimportowano {len(new_history.get_all_entries())} wersji")
    print(f"   ✓ Ostatnia wersja: {new_history.get_latest().description}")


def demo_templates():
    """Demonstrate template functionality."""
    print("\n" + "="*60)
    print("DEMONSTRACJA SZABLONÓW")
    print("="*60)
    
    # Define templates inline to avoid tkinter import
    templates = {
        "Dach dwuspadowy - standard": {
            "description": "Standard dwuspadowy",
            "items": [
                {"name": "Blachodachówka modułowa", "quantity": 100.0, "unit": "m²", "price_unit_net": 35.0},
                {"name": "Łaty drewniane 40x60", "quantity": 150.0, "unit": "mb", "price_unit_net": 4.5},
                {"name": "Kontrłaty 40x60", "quantity": 140.0, "unit": "mb", "price_unit_net": 4.5},
                {"name": "Membrana wstępnego krycia", "quantity": 120.0, "unit": "m²", "price_unit_net": 2.8},
                {"name": "Taśma uszczelniająca kalenicowa", "quantity": 12.0, "unit": "mb", "price_unit_net": 8.0},
                {"name": "Wkręty do blachodachówki", "quantity": 800.0, "unit": "szt", "price_unit_net": 0.35},
                {"name": "Robocizna montaż pokrycia", "quantity": 100.0, "unit": "m²", "price_unit_net": 25.0},
            ]
        },
        "System rynnowy kompletny": {
            "description": "Kompletny system rynnowy PVC",
            "items": [
                {"name": "Rynna PVC 125mm", "quantity": 40.0, "unit": "mb", "price_unit_net": 18.0},
                {"name": "Rura spustowa PVC 90mm", "quantity": 20.0, "unit": "mb", "price_unit_net": 15.0},
                {"name": "Łącznik rynny", "quantity": 10.0, "unit": "szt", "price_unit_net": 8.0},
                {"name": "Uchwyt rynny", "quantity": 30.0, "unit": "szt", "price_unit_net": 4.5},
            ]
        }
    }
    
    print(f"\nDostępne szablony ({len(templates)}):")
    for i, (name, template) in enumerate(templates.items(), 1):
        print(f"\n{i}. {name}")
        print(f"   Opis: {template['description']}")
        print(f"   Pozycje ({len(template['items'])}):")
        
        total = 0
        for item in template['items'][:5]:  # Show first 5 items
            value = item['quantity'] * item['price_unit_net']
            total += value
            print(f"      - {item['name']}: {item['quantity']} {item['unit']} × {item['price_unit_net']:.2f} zł = {value:.2f} zł")
        
        if len(template['items']) > 5:
            print(f"      ... i {len(template['items']) - 5} więcej")
        
        # Calculate total for all items
        total_all = sum(item['quantity'] * item['price_unit_net'] for item in template['items'])
        print(f"   Szacunkowa wartość netto: {total_all:.2f} zł")
    
    print("\n   UWAGA: W aplikacji dostępnych jest 6 szablonów:")
    print("      1. Dach dwuspadowy - standard")
    print("      2. Dach kopertowy - standard")
    print("      3. Remont pokrycia")
    print("      4. System rynnowy kompletny")
    print("      5. Obróbki blacharskie")
    print("      6. Pusty kosztorys")


def demo_checksum():
    """Demonstrate checksum calculation."""
    print("\n" + "="*60)
    print("DEMONSTRACJA WYKRYWANIA ZMIAN (CHECKSUM)")
    print("="*60)
    
    items1 = [
        {'name': 'Item A', 'quantity': 10, 'price': 5.0},
        {'name': 'Item B', 'quantity': 20, 'price': 3.0}
    ]
    
    items2 = [
        {'name': 'Item A', 'quantity': 10, 'price': 5.0},
        {'name': 'Item B', 'quantity': 20, 'price': 3.0}
    ]
    
    items3 = [
        {'name': 'Item A', 'quantity': 15, 'price': 5.0},  # Zmieniona ilość
        {'name': 'Item B', 'quantity': 20, 'price': 3.0}
    ]
    
    checksum1 = CostEstimateHistory.calculate_checksum(items1)
    checksum2 = CostEstimateHistory.calculate_checksum(items2)
    checksum3 = CostEstimateHistory.calculate_checksum(items3)
    
    print("\n1. Identyczne pozycje:")
    print(f"   Checksum 1: {checksum1}")
    print(f"   Checksum 2: {checksum2}")
    print(f"   Takie same: {'✓ TAK' if checksum1 == checksum2 else '✗ NIE'}")
    
    print("\n2. Zmienione pozycje (inna ilość):")
    print(f"   Checksum 1: {checksum1}")
    print(f"   Checksum 3: {checksum3}")
    print(f"   Takie same: {'✓ TAK' if checksum1 == checksum3 else '✗ NIE'}")
    
    print("\n   → Checksum pozwala szybko wykryć, czy kosztorys został zmieniony")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("WERYFIKACJA MANUALNA - NOWE FUNKCJE")
    print("Historia zmian kosztorysu i szablony")
    print("="*60)
    
    try:
        demo_history()
        demo_templates()
        demo_checksum()
        
        print("\n" + "="*60)
        print("✓ WSZYSTKIE DEMONSTRACJE ZAKOŃCZONE SUKCESEM")
        print("="*60)
        
        print("\nNowe funkcje są dostępne w aplikacji przez:")
        print("  • Menu → Plik → Historia zmian...")
        print("  • Menu → Plik → Utwórz z istniejącego...")
        print("\nHistoria jest automatycznie zapisywana przy każdym zapisie kosztorysu.")
        
    except Exception as e:
        print(f"\n✗ BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
