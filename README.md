# Ofertownik - Kalkulator Dachów

[![Build and Test](https://github.com/Majcher-creator/Ofertownik/workflows/Build%20and%20Test/badge.svg)](https://github.com/Majcher-creator/Ofertownik/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🏠 Profesjonalny Kalkulator Kosztorysów Dekarskich v4.7

Kompleksowa aplikacja desktopowa do tworzenia profesjonalnych kosztorysów ofertowych dla prac dekarskich.

### ✨ Główne funkcje

#### 💰 Moduł Kosztorysowy
- **Tworzenie kosztorysów** - Profesjonalne kosztorysy z podziałem na materiały i usługi
- **Zarządzanie pozycjami** - Dodawanie, edycja i usuwanie pozycji kosztorysowych
- **Obliczenia automatyczne** - Automatyczne obliczanie wartości netto, VAT i brutto
- **Transport** - Konfigurowalne dodawanie kosztów transportu
- **Podsumowania** - Grupowanie po stawkach VAT i kategoriach
- **Historia zmian** - Wersjonowanie kosztorysów z automatycznym zapisem przy każdym zapisie
- **Porównywanie wersji** - Szczegółowe porównanie dwóch wersji z wizualizacją różnic
- **Przywracanie wersji** - Możliwość przywrócenia dowolnej wcześniejszej wersji
- **Tworzenie z istniejącego** - Kopiowanie kosztorysów z opcjami wyboru danych
- **Szablony** - Predefiniowane szablony dla typowych prac dekarskich

#### 📐 Kalkulatory Techniczne
- **Pomiar Dachu** - Obliczenia dla dachów jednospadowych, dwuspadowych i kopertowych
- **System Rynnowy** - Zaawansowana kalkulacja rynien z wieloma systemami (PVC, stal, miedź, tytan-cynk)
  - Wybór z 4 predefiniowanych systemów rynnowych
  - Automatyczne przeliczanie akcesoriów na podstawie parametrów dachu
  - Edycja ilości i cen każdego akcesorium przed dodaniem do kosztorysu
  - Zapisywanie i wczytywanie własnych szablonów konfiguracji
  - Dialog przeglądu pozycji z możliwością wyboru co dodać
- **Obróbki Kominowe** - Obliczenia obróbek kominowych i czap
- **Obróbki Blacharskie** - Wiatrownice, okapnice, pasy nadrynnowe
- **Konstrukcja** - Obliczenia ilości drewna konstrukcyjnego

#### 👥 Zarządzanie Klientami
- **Baza klientów** - Przechowywanie danych kontaktowych
- **Walidacja NIP** - Automatyczna walidacja numerów NIP z sumą kontrolną
- **Historia** - Powiązanie kosztorysów z klientami

#### 📤 Eksport i Import
- **PDF** - Profesjonalne kosztorysy PDF z logo firmy
- **Podgląd PDF** - Podgląd wygenerowanego PDF przed zapisem
- **CSV** - Eksport do arkuszy kalkulacyjnych
- **JSON** - Zapisywanie i wczytywanie projektów
- **Word** - Eksport do edytowalnych dokumentów .docx (wkrótce)
- **Excel Import** - Import bazy materiałów z plików Excel/CSV

### 📄 Eksport

- **PDF** - Profesjonalny kosztorys ofertowy z logo firmy
- **Podgląd PDF** - Możliwość podglądu wygenerowanego PDF w domyślnej przeglądarce przed zapisem
- **CSV** - Eksport danych do arkusza kalkulacyjnego
- **JSON** - Zapisywanie i wczytywanie kosztorysów

### 🚀 Instalacja i Uruchomienie

#### Wymagania Systemowe
- Python 3.10 lub nowszy
- System operacyjny: Windows, macOS lub Linux
- Minimalne wymagania sprzętowe:
  - RAM: 4 GB
  - Miejsce na dysku: 200 MB

#### Instalacja

1. **Sklonuj repozytorium**
```bash
git clone https://github.com/Majcher-creator/Ofertownik.git
cd Ofertownik
```

2. **Utwórz wirtualne środowisko (opcjonalnie, ale zalecane)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Zainstaluj zależności**
```bash
pip install -r requirements.txt
```

4. **Skonfiguruj aplikację (opcjonalnie)**
```bash
# Skopiuj przykładowy plik konfiguracyjny
cp .env.example .env

# Edytuj .env i uzupełnij dane swojej firmy
```

#### Uruchomienie

```bash
# Uruchomienie aplikacji
python main_app044.py
```

#### Uruchomienie Testów

```bash
# Uruchom wszystkie testy
pytest

# Uruchom testy z pokryciem kodu
pytest --cov=app --cov-report=html

# Uruchom konkretny plik testów
pytest tests/test_roof_calculations.py -v
```

### 📁 Struktura projektu

```
Ofertownik/
├── app/                           # Główny pakiet aplikacji (nowa struktura modułowa)
│   ├── __init__.py
│   ├── models/                    # Modele danych
│   │   ├── client.py              # Model klienta
│   │   ├── cost_item.py           # Model pozycji kosztorysowej
│   │   ├── material.py            # Model materiału
│   │   └── gutter_models.py       # Modele systemów rynnowych (NEW)
│   ├── services/                  # Warstwa usług
│   │   ├── database.py            # Obsługa bazy danych SQLite
│   │   ├── file_manager.py        # Zarządzanie plikami JSON
│   │   ├── pdf_export.py          # Eksport do PDF
│   │   ├── csv_export.py          # Eksport do CSV
│   │   └── gutter_service.py      # Zarządzanie systemami rynnowymi (NEW)
│   ├── ui/                        # Komponenty interfejsu użytkownika
│   │   ├── styles.py              # Style i motywy (light/dark mode)
│   │   ├── dialogs.py             # Okna dialogowe
│   │   ├── gutter_tab.py          # Dialogi dla zakładki rynien (NEW)
│   │   └── tabs/                  # Zakładki aplikacji
│   │       ├── cost_tab.py        # Zakładka kosztorysu
│   │       ├── measurement_tab.py # Zakładka pomiarów
│   │       ├── gutter_tab.py      # Zakładka rynien
│   │       ├── chimney_tab.py     # Zakładka kominów
│   │       └── flashing_tab.py    # Zakładka obróbek
│   └── utils/                     # Narzędzia pomocnicze
│       ├── formatting.py          # Formatowanie wartości
│       └── validation.py          # Walidacja danych
├── tests/                         # Testy jednostkowe
│   ├── test_roof_calculations.py
│   ├── test_gutter_calculations.py
│   ├── test_gutter_models.py      # Testy modeli rynnowych (NEW)
│   ├── test_gutter_integration.py # Testy integracyjne (NEW)
│   ├── test_cost_calculations.py
│   └── test_validation.py
├── main_app044.py                 # Punkt wejścia aplikacji
├── roof_calculations.py           # Obliczenia geometrii dachów
├── gutter_calculations.py         # Obliczenia orynnowania
├── chimney_calculations.py        # Obliczenia obróbek kominowych
├── flashing_calculations.py       # Obliczenia obróbek blacharskich
├── timber_calculations.py         # Obliczenia drewna
├── gutter_systems.json            # Konfiguracja systemów rynnowych (NEW)
├── felt_calculations.py           # Obliczenia papy
├── cost_calculations.py           # Logika kosztorysowa
├── measurement_tab.py             # Moduł pomiaru figur
├── requirements.txt               # Zależności projektu
├── pytest.ini                     # Konfiguracja testów
├── .env.example                   # Przykładowa konfiguracja
├── .github/
│   └── workflows/
│       └── build.yml              # CI/CD workflow
└── README.md                      # Ta dokumentacja
```

### 🌧️ System Rynnowy - Nowa funkcjonalność (v4.8+)

#### Przegląd
Rozbudowana zakładka "Rynny" oferuje kompleksowe zarządzanie systemami rynnowymi z obsługą różnych typów i producentów.

#### Dostępne systemy
- **System PVC półokrągły 125mm** - Popularny system z tworzywa
- **System kwadratowy stalowy** - Stalowy system powlekany
- **System miedziany premium** - Ekskluzywny system z miedzi
- **System tytan-cynk** - Trwały i elegancki system

#### Kluczowe funkcje
1. **Wybór systemu** - Combobox z 4 predefiniowanymi systemami
2. **Automatyczne obliczenia** - Akcesoria przeliczane na podstawie parametrów dachu
3. **Edycja pozycji** - Możliwość zmiany ilości i ceny każdego akcesorium
4. **Przegląd przed dodaniem** - Dialog z tabelą pozycji do zatwierdzenia
5. **Szablony użytkownika** - Zapisywanie i wczytywanie własnych konfiguracji
6. **Kompatybilność wsteczna** - Stare kosztorysy działają bez zmian

#### Akcesoria wliczone w system
- Rynny (metry bieżące)
- Rury spustowe (metry bieżące)
- Haki rynnowe (automatycznie co 0.5m)
- Łączniki rynien (co 3m)
- Wyloty do rur (po jednym na rurę)
- Obejmy rurowe (co 2m)
- Kolanka (2 na rurę spustową)
- Zaślepki rynien
- Montaż systemu rynnowego

#### Szczegółowa dokumentacja
Zobacz [GUTTER_SYSTEM_DOCUMENTATION.md](GUTTER_SYSTEM_DOCUMENTATION.md) dla pełnej dokumentacji technicznej, przykładów użycia i API.

### 📜 Historia zmian i szablony

#### Historia wersji kosztorysu
- **Automatyczne wersjonowanie** - Każdy zapis tworzy snapshot w historii
- **Do 50 wersji** - Przechowywanie ostatnich 50 wersji dla każdego kosztorysu
- **Szczegółowe metadane** - Data, opis, liczba pozycji, wartość brutto
- **Wykrywanie zmian** - Checksum MD5 pozycji do szybkiej identyfikacji zmian

#### Porównywanie wersji
- **Wizualne porównanie** - Szczegółowe porównanie dwóch dowolnych wersji
- **Kategoryzacja zmian** - Podział na dodane, usunięte i zmienione pozycje
- **Analiza różnic** - Dokładna informacja o zmianach w ilościach, cenach i VAT
- **Przejrzysta prezentacja** - Zakładki dla różnych typów zmian

#### Przywracanie wersji
- **Cofanie zmian** - Możliwość przywrócenia dowolnej wcześniejszej wersji
- **Bezpieczeństwo** - Potwierdzenie przed przywróceniem
- **Pełne przywracanie** - Odtworzenie pozycji, klienta i ustawień

#### Tworzenie z istniejącego
- **Lista ostatnich** - Szybki dostęp do 10 ostatnio używanych kosztorysów
- **Przeglądanie plików** - Wybór dowolnego pliku .cost.json z podglądem
- **Opcje kopiowania**:
  - Kopiuj pozycje kosztorysowe
  - Kopiuj dane klienta
  - Kopiuj ustawienia (transport, VAT)
  - Wyzeruj ilości (pozostaw tylko nazwy i ceny)

#### Predefiniowane szablony
- **Dach dwuspadowy - standard** - Kompletny zestaw materiałów i robocizny
- **Dach kopertowy - standard** - Pakiet dla dachu kopertowego
- **Remont pokrycia** - Szablon do napraw i remontów
- **System rynnowy kompletny** - Pełna instalacja orynnowania PVC
- **Obróbki blacharskie** - Standardowe obróbki (okapniki, wiatrownice, pasy)
- **Pusty kosztorys** - Start od zera

### 🎨 Interfejs użytkownika

#### Cechy UI
- **Nowoczesny design** - Przejrzysty interfejs zgodny z najlepszymi praktykami UX
- **Kolorystyka branżowa** - Pomarańczowe akcenty nawiązujące do koloru dachówek
- **Tryb ciemny** - Opcjonalny dark mode dla wygody pracy (wkrótce)
- **Responsywność** - Automatyczne dostosowanie do rozmiaru okna
- **Ikony i oznaczenia** - Intuicyjna nawigacja z ikonami

#### Skróty klawiaturowe (wkrótce)
- `Ctrl+N` - Nowy kosztorys
- `Ctrl+S` - Zapisz kosztorys
- `Ctrl+O` - Otwórz kosztorys
- `Ctrl+P` - Eksport do PDF
- `F5` - Przelicz kosztorys
- `Ctrl+Q` - Zamknij aplikację

### 🔒 Bezpieczeństwo i Jakość

#### Zabezpieczenia
- **Walidacja danych** - Kompleksowa walidacja wszystkich danych wejściowych
- **Walidacja NIP** - Sprawdzanie poprawności numeru NIP z sumą kontrolną
- **Backup automatyczny** - Automatyczne kopie zapasowe przed modyfikacją danych
- **Bezpieczne pliki** - Sanityzacja nazw plików przed zapisem

#### Jakość kodu
- **Testy jednostkowe** - 70+ testów pokrywających kluczowe funkcjonalności (w tym 37 testów systemów rynnowych)
- **Type hints** - Pełne adnotacje typów dla lepszej dokumentacji i wykrywania błędów
- **PEP 8** - Kod zgodny ze standardami Pythona
- **CI/CD** - Automatyczne testy i budowanie na GitHub Actions

### 📚 Dokumentacja API

#### Główne moduły

##### `roof_calculations.py`
```python
from roof_calculations import calculate_gable_roof

# Oblicz dach dwuspadowy
result = calculate_gable_roof(
    dl=10.0,           # Długość w metrach
    szer=8.0,          # Szerokość w metrach
    angle_degrees=30.0, # Kąt nachylenia
    is_real_dimensions=False
)

print(result['powierzchnia_dachu'])  # Powierzchnia w m²
print(result['dlugosc_okapu'])       # Długość okapu w m
```

##### `cost_calculations.py`
```python
from cost_calculations import compute_totals

items = [
    {
        "name": "Dachówka ceramiczna",
        "quantity": 100.0,
        "unit": "m2",
        "price_unit_net": 45.0,
        "vat_rate": 8,
        "category": "material"
    }
]

result = compute_totals(items, transport_percent=3.0, transport_vat=23)
print(result['summary']['gross'])  # Wartość brutto
```

##### `app.utils.validation`
```python
from app.utils.validation import validate_nip, validate_cost_item

# Walidacja NIP
is_valid = validate_nip("5260250274")  # True

# Walidacja pozycji kosztorysowej
item = {"name": "Test", "quantity": 10, "price_unit_net": 50}
is_valid, error_msg = validate_cost_item(item)
```

### ❓ FAQ

**Q: Czy aplikacja wymaga połączenia z internetem?**  
A: Nie, aplikacja działa całkowicie offline. Wszystkie dane są przechowywane lokalnie.

**Q: Jak zaimportować własną bazę materiałów?**  
A: Możesz edytować plik `materialy_uslugi.json` lub użyć funkcji importu z Excel/CSV (wkrótce).

**Q: Czy mogę zmienić logo firmy na PDF?**  
A: Tak, zamień pliki `logo400x100.png` i `logo800x400.png` na własne w tym samym rozmiarze.

**Q: Jak przenieść dane na inny komputer?**  
A: Skopiuj pliki: `settings.json`, `materialy_uslugi.json` oraz wszystkie pliki `.cost.json`.

**Q: Czy aplikacja działa na macOS i Linux?**  
A: Tak, aplikacja jest w pełni wieloplatformowa.

**Q: Jak zgłosić błąd lub zaproponować nową funkcję?**  
A: Utwórz Issue na GitHubie: [github.com/Majcher-creator/Ofertownik/issues](https://github.com/Majcher-creator/Ofertownik/issues)

### 📝 Changelog

#### v4.7.0 (2024-12-27)
- ✨ Dodano modułową strukturę projektu (app/)
- ✨ Utworzono kompleksowe testy jednostkowe (49 testów)
- ✨ Dodano type hints do wszystkich modułów
- ✨ Implementacja walidacji z checksum NIP
- ✨ Dodano GitHub Actions CI/CD
- ✨ Rozszerzona dokumentacja README
- 🔧 Utworzono requirements.txt
- 🔧 Dodano .env.example dla konfiguracji
- 🗑️ Usunięto pliki backup (.bak)

#### v4.6.0
- 🎨 Ulepszony interfejs użytkownika
- 📐 Dodano zakładki dla różnych obliczeń
- 📄 Profesjonalny eksport PDF
- ✅ Lepsza walidacja danych

### 📄 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik LICENSE dla szczegółów.

### 👤 Autor i Kontakt

**VICTOR TOMASZ MAJCHERCZYK**  
Dąbrowa Górnicza  
*TYLKO DACHY TYLKO VICTOR*

---

### 🤝 Contributing

Zapraszamy do współpracy! Jeśli chcesz pomóc w rozwoju projektu:

1. Fork projektu
2. Utwórz branch dla swojej funkcji (`git checkout -b feature/AmazingFeature`)
3. Commit zmian (`git commit -m 'Add some AmazingFeature'`)
4. Push do brancha (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

#### Wytyczne dla kontrybutorów
- Pisz testy dla nowych funkcjonalności
- Przestrzegaj PEP 8
- Dodawaj type hints
- Aktualizuj dokumentację
- Upewnij się, że wszystkie testy przechodzą przed PR

### 🙏 Podziękowania

Dziękujemy wszystkim, którzy przyczynili się do rozwoju tego projektu!

### 📊 Status projektu

Projekt jest aktywnie rozwijany. Sprawdź [Issues](https://github.com/Majcher-creator/Ofertownik/issues) aby zobaczyć planowane funkcjonalności.

---

**Ostatnia aktualizacja:** Grudzień 2024
