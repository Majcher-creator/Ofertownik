# Rozbudowana funkcjonalność zakładki Orynnowanie

## Przegląd

Zakładka "Rynny" została rozbudowana o kompleksowy system zarządzania różnymi typami systemów rynnowych, z możliwością edycji akcesoriów, zapisywania własnych szablonów i precyzyjnego kontrolowania kosztorysu.

## Nowe funkcjonalności

### 1. Wybór systemu rynnowego

Aplikacja oferuje predefiniowane systemy rynnowe:

- **System PVC półokrągły 125mm** - popularny system z tworzywa PVC
- **System kwadratowy stalowy** - stalowy system o przekroju kwadratowym
- **System miedziany premium** - ekskluzywny system z miedzi
- **System tytan-cynk** - trwały system z tytanu-cynku

Każdy system zawiera:
- Własny zestaw akcesoriów
- Dedykowane ceny dla każdego elementu
- Automatyczne przeliczanie ilości na podstawie parametrów dachu

### 2. Zarządzanie akcesoriami

#### Automatyczne przeliczanie

Po wprowadzeniu parametrów:
- Długość okapu [m]
- Wysokość dachu (rury spustowej) [m]
- Liczba rur spustowych (opcjonalnie, 0=auto)

System automatycznie oblicza ilości dla:
- Rynny (długość w metrach bieżących)
- Rury spustowe (długość w metrach bieżących)
- Haki rynnowe (co 0.5m)
- Łączniki rynien (co 3m)
- Wyloty do rur (po jednym na rurę spustową)
- Obejmy rurowe (co 2m)
- Kolanka (2 na każdą rurę spustową)
- Zaślepki (minimum 2)
- Montaż systemu rynnowego

#### Ręczna edycja

Użytkownik może:
- Dwukrotnie kliknąć na akcesorium w tabeli
- Użyć przycisku "Edytuj wybraną"
- Zmienić ilość i cenę jednostkową dla każdego elementu

### 3. Szablony użytkownika

#### Zapisywanie szablonu

1. Wybierz system rynnowy
2. Oblicz akcesoria dla dachu
3. Opcjonalnie zmodyfikuj ilości lub ceny
4. Kliknij "💾 Zapisz szablon"
5. Podaj nazwę szablonu (np. "Dom jednorodzinny standardowy")

Szablon zapisuje:
- Wybrany system rynnowy
- Wszystkie akcesoria z ich ilościami i cenami
- Datę utworzenia

#### Wczytywanie szablonu

1. Kliknij "📂 Wczytaj szablon"
2. Wybierz szablon z listy
3. System automatycznie załaduje zapisaną konfigurację

### 4. Dodawanie do kosztorysu

Po obliczeniu akcesoriów:

1. Kliknij "➕ Dodaj pozycje do kosztorysu"
2. Otworzy się dialog przeglądu z tabelą wszystkich akcesoriów
3. W dialogu możesz:
   - Zaznaczyć/odznaczyć pozycje do dodania
   - Edytować ilość i cenę dla wybranej pozycji
   - Użyć przycisków "Zaznacz wszystkie" / "Odznacz wszystkie"
4. Kliknij "Dodaj do kosztorysu"
5. Wybrane pozycje zostaną dodane do zakładki kosztorysowej

## Struktura techniczna

### Modele danych

#### GutterAccessory
```python
@dataclass
class GutterAccessory:
    name: str                    # Nazwa akcesorium
    unit: str                    # Jednostka miary (mb, szt.)
    price_unit_net: float        # Cena jednostkowa netto
    quantity: float = 0.0        # Ilość
    vat_rate: int = 8           # Stawka VAT
    category: str = "material"   # Kategoria (material/service)
    auto_calculate: bool = True  # Czy auto-obliczać ilość
```

#### GutterSystem
```python
@dataclass
class GutterSystem:
    name: str                           # Nazwa systemu
    system_type: str                    # Typ (pvc, steel, copper, zinc-titanium)
    description: str = ""               # Opis
    accessories: List[GutterAccessory]  # Lista akcesoriów
```

#### GutterTemplate
```python
@dataclass
class GutterTemplate:
    name: str              # Nazwa szablonu
    system: GutterSystem   # Zapisany system z konfiguracją
    is_predefined: bool    # Czy szablon systemowy
    created_at: str        # Data utworzenia
```

### Serwis

#### GutterSystemManager

Główna klasa zarządzająca systemami:

```python
manager = GutterSystemManager()

# Pobranie dostępnych systemów
systems = manager.get_all_systems()
system = manager.get_system_by_name("System PVC półokrągły 125mm")

# Obliczanie akcesoriów
calculated = manager.calculate_accessories(
    system,
    okap_length_m=20.0,
    roof_height_m=5.0,
    num_downpipes=2
)

# Zapisywanie szablonu
template = GutterTemplate(name="Mój szablon", system=calculated)
manager.save_user_template(template)

# Wczytywanie szablonów
templates = manager.get_all_templates()
```

### Pliki konfiguracyjne

#### gutter_systems.json

Zawiera predefiniowane systemy i szablony użytkownika:

```json
{
  "predefined_systems": [
    {
      "name": "System PVC półokrągły 125mm",
      "system_type": "pvc",
      "description": "...",
      "accessories": [...]
    }
  ],
  "user_templates": [
    {
      "name": "Mój szablon",
      "system": {...},
      "created_at": "2024-01-01T12:00:00"
    }
  ]
}
```

## Użycie w aplikacji

### W zakładce Rynny

```python
# main_app044.py

# Inicjalizacja managera
from app.services.gutter_service import GutterSystemManager
self.gutter_manager = GutterSystemManager()

# Wybór systemu
self.gutter_system_var = tk.StringVar()
system_combo = ttk.Combobox(
    frame,
    textvariable=self.gutter_system_var,
    values=self.gutter_manager.get_system_names()
)

# Obliczanie
def calculate_gutters(self):
    system = self.gutter_manager.get_system_by_name(
        self.gutter_system_var.get()
    )
    calculated = self.gutter_manager.calculate_accessories(
        system,
        self.gutter_okap_length.get(),
        self.gutter_roof_height.get(),
        self.gutter_num_downpipes.get()
    )
```

### Dialog przeglądu akcesoriów

```python
from app.ui.gutter_tab import GutterAccessoriesDialog

dialog = GutterAccessoriesDialog(parent, accessories)
if dialog.result:
    # dialog.result zawiera listę wybranych akcesoriów
    for acc in dialog.result:
        # Dodaj do kosztorysu
        add_cost_item(acc)
```

## Kompatybilność wsteczna

Stara funkcjonalność jest zachowana:

```python
# Stary sposób - nadal działa
from gutter_calculations import calculate_guttering

results = calculate_guttering(okap_length_m=20.0, roof_height_m=5.0)
# Zwraca słownik z obliczeniami
```

Aplikacja automatycznie wykrywa dostępność nowego systemu i używa odpowiedniej implementacji.

## Testy

### Testy jednostkowe

```bash
# Testy modeli
pytest tests/test_gutter_models.py -v

# Testy starych obliczeń
pytest tests/test_gutter_calculations.py -v
```

### Testy integracyjne

```bash
# Kompletny workflow
pytest tests/test_gutter_integration.py -v
```

## Przykłady użycia

### Przykład 1: Podstawowe użycie

```python
from app.services.gutter_service import GutterSystemManager

manager = GutterSystemManager()

# Wybierz system PVC
system = manager.get_system_by_name("System PVC półokrągły 125mm")

# Oblicz dla domu o okapie 25m i wysokości 6m
calculated = manager.calculate_accessories(system, 25.0, 6.0)

# Sprawdź wyniki
for acc in calculated.accessories:
    if acc.quantity > 0:
        total = acc.quantity * acc.price_unit_net
        print(f"{acc.name}: {acc.quantity} {acc.unit} x {acc.price_unit_net} zł = {total:.2f} zł")
```

### Przykład 2: Własny szablon

```python
from app.services.gutter_service import GutterSystemManager
from app.models.gutter_models import GutterTemplate

manager = GutterSystemManager()

# Przygotuj system
system = manager.get_system_by_name("System PVC półokrągły 125mm")
calculated = manager.calculate_accessories(system, 30.0, 7.0)

# Zmodyfikuj ceny (np. promocja)
for acc in calculated.accessories:
    acc.price_unit_net *= 0.9  # 10% rabatu

# Zapisz jako szablon
template = GutterTemplate(
    name="Promocja zimowa 2024",
    system=calculated
)
manager.save_user_template(template)
```

### Przykład 3: Dodawanie do kosztorysu

```python
# Po obliczeniu w UI
accessories = calculated_system.accessories

# Filtruj akcesoria z ilością > 0
items_to_add = [acc for acc in accessories if acc.quantity > 0]

# Pokaż dialog przeglądu
from app.ui.gutter_tab import GutterAccessoriesDialog
dialog = GutterAccessoriesDialog(root, items_to_add)

if dialog.result:
    # Dodaj wybrane do kosztorysu
    for acc in dialog.result:
        cost_item = {
            "name": acc.name,
            "quantity": acc.quantity,
            "unit": acc.unit,
            "price_unit_net": acc.price_unit_net,
            "vat_rate": acc.vat_rate,
            "category": acc.category,
            "note": ""
        }
        cost_items.append(cost_item)
```

## Najczęstsze problemy

### Problem: Szablony nie zapisują się

**Rozwiązanie**: Sprawdź uprawnienia do zapisu w katalogu aplikacji. Plik `gutter_systems.json` musi być zapisywalny.

### Problem: Brak systemów w liście

**Rozwiązanie**: Upewnij się, że plik `gutter_systems.json` istnieje w katalogu głównym aplikacji. Jeśli nie, zostanie utworzony automatycznie przy pierwszym uruchomieniu.

### Problem: Akcesoria nie przeliczają się

**Rozwiązanie**: Sprawdź, czy akcesoria mają ustawioną flagę `auto_calculate: true` w pliku konfiguracyjnym.

## Rozwój funkcjonalności

### Planowane ulepszenia

1. Import systemów z plików Excel/CSV
2. Eksport szablonów do udostępniania
3. Kalkulatory zaawansowane (różne spadki, kształty)
4. Wizualizacja systemu rynnowego
5. Integracja z bazą producentów i ich katalogami

## Licencja i autorzy

Część projektu Ofertownik - Kalkulator Dachów v4.7+

Implementacja: GitHub Copilot & Contributors
Data: 2024-2026
