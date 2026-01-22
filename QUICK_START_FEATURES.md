# Quick Start - Nowe Funkcjonalności Ofertownik

## 🚀 Szybki Start

Ten dokument przedstawia proste przykłady użycia nowych funkcjonalności.

---

## 1. 💰 Kalkulator Marży

### Podstawowe użycie
```python
from app.services.margin_calculator import MarginSettings, MarginCalculator
from app.models.cost_item import CostItem

# Ustawienia marży
settings = MarginSettings(global_margin_percent=20.0)
settings.set_group_margin("Materiały", 25.0)
settings.set_group_margin("Usługi", 30.0)

# Kalkulator
calculator = MarginCalculator(settings)

# Pozycje z cenami zakupu
items = [
    CostItem(
        name="Dachówka",
        quantity=100,
        unit="szt",
        price_unit_net=0,
        purchase_price=50.0,
        group="Materiały"
    ),
    CostItem(
        name="Montaż",
        quantity=1,
        unit="usł",
        price_unit_net=0,
        purchase_price=1000.0,
        group="Usługi"
    )
]

# Oblicz ceny sprzedaży
calculator.apply_margin_to_items(items)

print(f"Dachówka - sprzedaż: {items[0].price_unit_net} zł")  # 62.50 (25% marży)
print(f"Montaż - sprzedaż: {items[1].price_unit_net} zł")     # 1300.00 (30% marży)

# Statystyki
summary = calculator.get_margin_summary(items)
print(f"Całkowita marża: {summary['total_margin_value']} zł")
```

---

## 2. 📄 Szablony Kosztorysów

### Zapisywanie szablonu
```python
from app.services.template_service import TemplateManager

manager = TemplateManager()

# Dane kosztorysu
items = [
    {'name': 'Dachówka ceramiczna', 'quantity': 100, 'price': 50},
    {'name': 'Łaty drewniane', 'quantity': 50, 'price': 15},
    {'name': 'Montaż', 'quantity': 1, 'price': 2000}
]

# Zapis jako szablon
template = manager.save_template(
    name="Dach dwuspadowy - ceramika",
    description="Standardowy dach dwuspadowy z dachówką ceramiczną",
    items=items,
    groups=["Materiały", "Robocizna"]
)

print(f"Szablon zapisany: {template.id}")
```

### Wczytywanie szablonu
```python
# Lista szablonów
templates = manager.list_templates()
for t in templates:
    print(f"{t.name} - {len(t.items)} pozycji")

# Wczytaj szablon
loaded = manager.load_template(templates[0].id)
print(f"Wczytano: {loaded.name}")
print(f"Pozycji: {len(loaded.items)}")

# Wyszukiwanie
results = manager.search_templates("dach")
print(f"Znaleziono {len(results)} szablonów")
```

---

## 3. 📜 Wersjonowanie

### Tworzenie wersji
```python
from app.services.version_service import VersionManager

manager = VersionManager(author="Jan Kowalski")

# Pierwsza wersja
snapshot1 = {
    'items': [{'name': 'Pozycja 1', 'price': 100}],
    'total_gross': 123,
    'groups': ['Materiały']
}

v1 = manager.create_version("kosztorys-001", snapshot1)
print(f"Wersja {v1.version_number}: {v1.description}")

# Druga wersja (ze zmianami)
snapshot2 = {
    'items': [
        {'name': 'Pozycja 1', 'price': 100},
        {'name': 'Pozycja 2', 'price': 150}
    ],
    'total_gross': 307.5,
    'groups': ['Materiały']
}

v2 = manager.create_version("kosztorys-001", snapshot2)
print(f"Wersja {v2.version_number}: {v2.description}")
print(f"Zmiany: {', '.join(v2.changes)}")
```

### Przywracanie wersji
```python
# Historia
history = manager.get_history("kosztorys-001")
print(f"Wersji w historii: {len(history.versions)}")

# Przywróć poprzednią wersję
restored = manager.restore_version("kosztorys-001", version_number=1)
print(f"Przywrócono wersję z {len(restored['items'])} pozycjami")

# Porównaj wersje
comparison = manager.compare_versions("kosztorys-001", 1, 2)
print(f"Różnic: {comparison['change_count']}")
for change in comparison['changes']:
    print(f"  - {change}")
```

---

## 4. 📎 Załączniki

### Dodawanie załączników
```python
from app.services.attachment_service import AttachmentManager

manager = AttachmentManager()

# Dodaj zdjęcie
attachment = manager.add_attachment(
    file_path="/path/to/photo.jpg",
    description="Zdjęcie dachu przed remontem",
    linked_item_id=None  # Dla całego kosztorysu
)

print(f"Dodano: {attachment.filename}")
print(f"Rozmiar: {attachment.get_display_size()}")
print(f"Miniatura: {attachment.thumbnail_path}")

# Załącznik do konkretnej pozycji
attachment2 = manager.add_attachment(
    file_path="/path/to/spec.pdf",
    description="Specyfikacja techniczna",
    linked_item_id="item-123"
)
```

### Zarządzanie załącznikami
```python
# Statystyki
stats = manager.get_storage_stats()
print(f"Plików: {stats['file_count']}")
print(f"Zajętość: {stats['total_size_mb']} MB")

# Filtrowanie załączników
all_attachments = [...]  # Lista załączników

# Załączniki kosztorysu
estimate_files = manager.get_attachments_for_estimate(all_attachments)
print(f"Załączników kosztorysu: {len(estimate_files)}")

# Załączniki pozycji
item_files = manager.get_attachments_for_item(all_attachments, "item-123")
print(f"Załączników pozycji: {len(item_files)}")
```

---

## 5. 🔧 Obróbki Blacharskie

### Podstawowe użycie
```python
from app.services.flashing_service import FlashingManager

manager = FlashingManager()

# Lista profili
profiles = manager.get_all_profiles()
for p in profiles:
    print(f"{p.name} - {p.price_per_meter} zł/mb")

# Kalkulator
result = manager.calculate_sheet_requirements("okap-standard", length_m=12.5)
print(f"\nObróbka okapowa - 12.5 mb:")
print(f"  Powierzchnia: {result['area_m2']} m²")
print(f"  Masa: {result['weight_kg']} kg")
print(f"  Cena: {result['total_price']} zł")
```

### Własne profile
```python
# Dodaj własny profil
custom = manager.add_custom_profile(
    name="Obróbka specjalna 350mm",
    description="Niestandardowy profil dla projektu X",
    development_width=350.0,
    material_type="aluminium",
    price_per_meter=58.0,
    unit_conversions={
        "m2_per_meter": 0.35,
        "kg_per_meter": 1.6
    }
)

print(f"Utworzono profil: {custom.name}")

# Użyj nowego profilu
calc = manager.calculate_sheet_requirements(custom.id, length_m=10.0)
print(f"Cena: {calc['total_price']} zł")
```

### Materiały
```python
# Lista materiałów
materials = manager.materials
for m in materials:
    print(f"{m.name} - {m.price_per_m2} zł/m²")

# Dodaj nowy materiał
material = manager.add_material(
    name="Blacha tytanowo-cynkowa 0.7mm",
    material_type="tytan-cynk",
    thickness_mm=0.7,
    coating="naturalna",
    price_per_m2=165.0,
    price_per_kg=38.0,
    weight_per_m2=5.2,
    color="szary metaliczny"
)

# Oblicz cenę
price_area = material.calculate_price_by_area(5.0)  # 825 zł
price_weight = material.calculate_price_by_weight(10.0)  # 380 zł
```

---

## 6. 📁 Grupowanie

### Użycie grup
```python
from app.models.cost_item import CostItem

# Pozycje z grupami
items = [
    CostItem(
        name="Dachówka",
        quantity=100,
        unit="szt",
        price_unit_net=50,
        group="Materiały"
    ),
    CostItem(
        name="Rynna",
        quantity=15,
        unit="mb",
        price_unit_net=35,
        group="Materiały"
    ),
    CostItem(
        name="Montaż pokrycia",
        quantity=1,
        unit="usł",
        price_unit_net=3000,
        group="Robocizna"
    )
]

# Grupowanie
from collections import defaultdict

grouped = defaultdict(list)
for item in items:
    grouped[item.group].append(item)

# Podsumowania per grupa
for group, group_items in grouped.items():
    total = sum(i.price_unit_net * i.quantity for i in group_items)
    print(f"{group}: {total} zł ({len(group_items)} poz.)")
```

---

## 🎨 Kolory UI

### Nowa paleta
```python
# W stylach (app/ui/styles.py)
COLORS = {
    'accent': '#F1C40F',         # Słoneczny żółty
    'accent_dark': '#D4AC0D',    # Ciemniejszy żółty
    'table_header': '#F9E79F',   # Jasny żółty
    'table_alt': '#FEFCF3',      # Bardzo jasny żółty
    # ... pozostałe kolory
}
```

Wszystkie elementy UI (przyciski, nagłówki, tabele, PDF) używają nowej palety żółtej.

---

## 🔗 Integracja

### Przykład pełnego workflow
```python
# 1. Konfiguracja marży
from app.services.margin_calculator import MarginSettings, MarginCalculator

margin_settings = MarginSettings(global_margin_percent=22.0)
margin_settings.set_group_margin("Materiały", 25.0)
calculator = MarginCalculator(margin_settings)

# 2. Tworzenie pozycji z grupami
from app.models.cost_item import CostItem

items = [
    CostItem(
        name="Dachówka ceramiczna",
        quantity=100,
        unit="szt",
        price_unit_net=0,
        purchase_price=45.0,
        group="Materiały"
    )
]

# 3. Aplikuj marże
calculator.apply_margin_to_items(items)

# 4. Zapisz jako szablon
from app.services.template_service import TemplateManager

template_mgr = TemplateManager()
template = template_mgr.save_template(
    name="Kosztorys z marżą",
    description="Szablon z automatyczną marżą",
    items=[item.to_dict() for item in items],
    groups=["Materiały"]
)

# 5. Utwórz wersję
from app.services.version_service import VersionManager

version_mgr = VersionManager(author="System")
snapshot = {
    'items': [item.to_dict() for item in items],
    'total_gross': sum(i.total_gross for i in items),
    'groups': ["Materiały"]
}
version = version_mgr.create_version("est-001", snapshot)

# 6. Dodaj załączniki
from app.services.attachment_service import AttachmentManager

attach_mgr = AttachmentManager()
attachment = attach_mgr.add_attachment(
    file_path="photo.jpg",
    description="Zdjęcie lokalizacji",
    linked_item_id=None
)

print("✅ Kosztorys gotowy!")
print(f"   Szablon: {template.name}")
print(f"   Wersja: {version.version_number}")
print(f"   Załączników: 1")
```

---

## 📖 Dalsze informacje

Zobacz `FEATURE_IMPLEMENTATION_GUIDE.md` dla:
- Szczegółowej dokumentacji API
- Zaawansowanych przykładów
- Wzorców projektowych
- Planów rozwoju

---

## 💡 Wskazówki

1. **Automatyczne katalogi**: Wszystkie potrzebne katalogi (`templates/`, `attachments/`) są tworzone automatycznie
2. **Konfiguracja**: Pliki JSON (`flashing_profiles.json`) są generowane przy pierwszym użyciu
3. **Testy**: Uruchom `pytest tests/` aby zweryfikować instalację
4. **Miniaturki**: Wymagają Pillow (PIL) - już w requirements.txt

---

## ⚡ Najlepsze praktyki

- Używaj wersjonowania przy każdej istotnej zmianie
- Twórz szablony dla powtarzalnych kosztorysów
- Grupuj pozycje logicznie (Materiały, Robocizna, etc.)
- Przypisuj marże per grupa dla lepszej kontroli
- Dodawaj załączniki do pozycji wymagających wizualizacji

---

**Gotowe do użycia!** 🚀
