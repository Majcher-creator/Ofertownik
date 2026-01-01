"""
Dialog for creating a new cost estimate based on an existing one or template.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, Dict, Any, List
import json
import os


class CreateFromExistingDialog(tk.Toplevel):
    """
    Dialog for creating a cost estimate from existing file or template.
    """
    
    # Predefined templates
    TEMPLATES = {
        "Dach dwuspadowy - standard": {
            "description": "Standard dwuspadowy",
            "items": [
                {"name": "Blachodachówka modułowa", "quantity": 100.0, "unit": "m²", "price_unit_net": 35.0, "vat_rate": 23, "category": "material"},
                {"name": "Łaty drewniane 40x60", "quantity": 150.0, "unit": "mb", "price_unit_net": 4.5, "vat_rate": 23, "category": "material"},
                {"name": "Kontrłaty 40x60", "quantity": 140.0, "unit": "mb", "price_unit_net": 4.5, "vat_rate": 23, "category": "material"},
                {"name": "Membrana wstępnego krycia", "quantity": 120.0, "unit": "m²", "price_unit_net": 2.8, "vat_rate": 23, "category": "material"},
                {"name": "Taśma uszczelniająca kalenicowa", "quantity": 12.0, "unit": "mb", "price_unit_net": 8.0, "vat_rate": 23, "category": "material"},
                {"name": "Wkręty do blachodachówki", "quantity": 800.0, "unit": "szt", "price_unit_net": 0.35, "vat_rate": 23, "category": "material"},
                {"name": "Robocizna montaż pokrycia", "quantity": 100.0, "unit": "m²", "price_unit_net": 25.0, "vat_rate": 23, "category": "service"},
            ]
        },
        "Dach kopertowy - standard": {
            "description": "Standard kopertowy",
            "items": [
                {"name": "Blachodachówka modułowa", "quantity": 120.0, "unit": "m²", "price_unit_net": 35.0, "vat_rate": 23, "category": "material"},
                {"name": "Łaty drewniane 40x60", "quantity": 180.0, "unit": "mb", "price_unit_net": 4.5, "vat_rate": 23, "category": "material"},
                {"name": "Kontrłaty 40x60", "quantity": 170.0, "unit": "mb", "price_unit_net": 4.5, "vat_rate": 23, "category": "material"},
                {"name": "Membrana wstępnego krycia", "quantity": 140.0, "unit": "m²", "price_unit_net": 2.8, "vat_rate": 23, "category": "material"},
                {"name": "Taśma uszczelniająca kalenicowa", "quantity": 15.0, "unit": "mb", "price_unit_net": 8.0, "vat_rate": 23, "category": "material"},
                {"name": "Pas startowy", "quantity": 40.0, "unit": "mb", "price_unit_net": 12.0, "vat_rate": 23, "category": "material"},
                {"name": "Wkręty do blachodachówki", "quantity": 1000.0, "unit": "szt", "price_unit_net": 0.35, "vat_rate": 23, "category": "material"},
                {"name": "Robocizna montaż pokrycia", "quantity": 120.0, "unit": "m²", "price_unit_net": 28.0, "vat_rate": 23, "category": "service"},
            ]
        },
        "Remont pokrycia": {
            "description": "Remont istniejącego pokrycia",
            "items": [
                {"name": "Demontaż starego pokrycia", "quantity": 100.0, "unit": "m²", "price_unit_net": 8.0, "vat_rate": 23, "category": "service"},
                {"name": "Naprawa łacenia", "quantity": 50.0, "unit": "mb", "price_unit_net": 12.0, "vat_rate": 23, "category": "service"},
                {"name": "Blachodachówka modułowa", "quantity": 100.0, "unit": "m²", "price_unit_net": 35.0, "vat_rate": 23, "category": "material"},
                {"name": "Membrana wstępnego krycia", "quantity": 110.0, "unit": "m²", "price_unit_net": 2.8, "vat_rate": 23, "category": "material"},
                {"name": "Wymiana uszkodzonych łat", "quantity": 30.0, "unit": "mb", "price_unit_net": 15.0, "vat_rate": 23, "category": "service"},
                {"name": "Robocizna montaż pokrycia", "quantity": 100.0, "unit": "m²", "price_unit_net": 25.0, "vat_rate": 23, "category": "service"},
            ]
        },
        "System rynnowy kompletny": {
            "description": "Kompletny system rynnowy PVC",
            "items": [
                {"name": "Rynna PVC 125mm", "quantity": 40.0, "unit": "mb", "price_unit_net": 18.0, "vat_rate": 23, "category": "material"},
                {"name": "Rura spustowa PVC 90mm", "quantity": 20.0, "unit": "mb", "price_unit_net": 15.0, "vat_rate": 23, "category": "material"},
                {"name": "Łącznik rynny", "quantity": 10.0, "unit": "szt", "price_unit_net": 8.0, "vat_rate": 23, "category": "material"},
                {"name": "Uchwyt rynny", "quantity": 30.0, "unit": "szt", "price_unit_net": 4.5, "vat_rate": 23, "category": "material"},
                {"name": "Kolano 87°", "quantity": 8.0, "unit": "szt", "price_unit_net": 12.0, "vat_rate": 23, "category": "material"},
                {"name": "Lejek rynnowy", "quantity": 4.0, "unit": "szt", "price_unit_net": 15.0, "vat_rate": 23, "category": "material"},
                {"name": "Obejma rury spustowej", "quantity": 15.0, "unit": "szt", "price_unit_net": 6.0, "vat_rate": 23, "category": "material"},
                {"name": "Montaż systemu rynnowego", "quantity": 1.0, "unit": "kpl", "price_unit_net": 800.0, "vat_rate": 23, "category": "service"},
            ]
        },
        "Obróbki blacharskie": {
            "description": "Kompletne obróbki blacharskie",
            "items": [
                {"name": "Okapnik", "quantity": 40.0, "unit": "mb", "price_unit_net": 18.0, "vat_rate": 23, "category": "material"},
                {"name": "Wiatrownica szczytowa", "quantity": 25.0, "unit": "mb", "price_unit_net": 22.0, "vat_rate": 23, "category": "material"},
                {"name": "Pas nadrynnowy", "quantity": 40.0, "unit": "mb", "price_unit_net": 16.0, "vat_rate": 23, "category": "material"},
                {"name": "Obróbka komina", "quantity": 4.0, "unit": "mb", "price_unit_net": 80.0, "vat_rate": 23, "category": "material"},
                {"name": "Obróbka okna dachowego", "quantity": 2.0, "unit": "kpl", "price_unit_net": 120.0, "vat_rate": 23, "category": "material"},
                {"name": "Montaż obróbek", "quantity": 1.0, "unit": "kpl", "price_unit_net": 600.0, "vat_rate": 23, "category": "service"},
            ]
        },
        "Pusty kosztorys": {
            "description": "Pusty kosztorys - brak pozycji",
            "items": []
        }
    }
    
    def __init__(self, parent, recent_files: List[str],
                 on_create: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize the create from existing dialog.
        
        Args:
            parent: Parent window
            recent_files: List of recently used file paths
            on_create: Callback function when creating new estimate
        """
        super().__init__(parent)
        self.recent_files = recent_files
        self.on_create = on_create
        self.selected_data: Optional[Dict[str, Any]] = None
        
        self.title("Utwórz kosztorys z istniejącego")
        self.geometry("800x650")
        self.transient(parent)
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the dialog UI."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                                text="Utwórz kosztorys na podstawie istniejącego",
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab 1: Recent files
        self.recent_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.recent_tab, text="Ostatnie kosztorysy")
        self._create_recent_tab()
        
        # Tab 2: Browse files
        self.browse_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.browse_tab, text="Wybierz plik")
        self._create_browse_tab()
        
        # Tab 3: Templates
        self.templates_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.templates_tab, text="Szablony")
        self._create_templates_tab()
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Opcje kopiowania", padding="10")
        options_frame.pack(fill='x', pady=(10, 0))
        
        self.copy_items = tk.BooleanVar(value=True)
        self.copy_client = tk.BooleanVar(value=True)
        self.copy_settings = tk.BooleanVar(value=True)
        self.zero_quantities = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Kopiuj pozycje kosztorysowe",
                       variable=self.copy_items).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Kopiuj dane klienta",
                       variable=self.copy_client).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Kopiuj ustawienia (transport, VAT)",
                       variable=self.copy_settings).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Wyzeruj ilości (zostaw tylko nazwy i ceny)",
                       variable=self.zero_quantities).pack(anchor='w', pady=2)
        
        # Name frame
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(name_frame, text="Nazwa nowego kosztorysu:").pack(side='left', padx=5)
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=40).pack(side='left', fill='x', expand=True, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Utwórz", 
                  command=self._create_estimate,
                  style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Anuluj", 
                  command=self.destroy).pack(side='right', padx=5)
        
    def _create_recent_tab(self):
        """Create the recent files tab."""
        # Info label
        info_label = ttk.Label(self.recent_tab, 
                              text="Wybierz z ostatnio używanych plików:",
                              font=('Segoe UI', 10))
        info_label.pack(pady=(0, 10))
        
        # Listbox for recent files
        list_frame = ttk.Frame(self.recent_tab)
        list_frame.pack(fill='both', expand=True)
        
        scroll_y = ttk.Scrollbar(list_frame, orient='vertical')
        scroll_x = ttk.Scrollbar(list_frame, orient='horizontal')
        
        self.recent_listbox = tk.Listbox(list_frame,
                                         yscrollcommand=scroll_y.set,
                                         xscrollcommand=scroll_x.set,
                                         font=('Segoe UI', 10))
        
        scroll_y.config(command=self.recent_listbox.yview)
        scroll_x.config(command=self.recent_listbox.xview)
        
        self.recent_listbox.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Load recent files
        for filepath in self.recent_files:
            if os.path.exists(filepath):
                display_name = os.path.basename(filepath)
                self.recent_listbox.insert('end', f"{display_name} ({filepath})")
        
        if not self.recent_files:
            self.recent_listbox.insert('end', "Brak ostatnio używanych plików")
        
        # Bind selection
        self.recent_listbox.bind('<<ListboxSelect>>', self._on_recent_select)
        
    def _create_browse_tab(self):
        """Create the browse files tab."""
        # Info label
        info_label = ttk.Label(self.browse_tab, 
                              text="Wybierz plik kosztorysu (.cost.json):",
                              font=('Segoe UI', 10))
        info_label.pack(pady=(0, 10))
        
        # File path frame
        path_frame = ttk.Frame(self.browse_tab)
        path_frame.pack(fill='x', pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.file_path_var, 
                 state='readonly').pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(path_frame, text="Przeglądaj...", 
                  command=self._browse_file).pack(side='left', padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self.browse_tab, text="Podgląd", padding="10")
        preview_frame.pack(fill='both', expand=True)
        
        self.preview_text = tk.Text(preview_frame, height=15, wrap='word',
                                    state='disabled', font=('Segoe UI', 9))
        preview_scroll = ttk.Scrollbar(preview_frame, orient='vertical',
                                      command=self.preview_text.yview)
        self.preview_text.config(yscrollcommand=preview_scroll.set)
        
        self.preview_text.pack(side='left', fill='both', expand=True)
        preview_scroll.pack(side='right', fill='y')
        
    def _create_templates_tab(self):
        """Create the templates tab."""
        # Info label
        info_label = ttk.Label(self.templates_tab, 
                              text="Wybierz szablon do utworzenia kosztorysu:",
                              font=('Segoe UI', 10))
        info_label.pack(pady=(0, 10))
        
        # Templates listbox
        list_frame = ttk.Frame(self.templates_tab)
        list_frame.pack(fill='both', expand=True)
        
        scroll_y = ttk.Scrollbar(list_frame, orient='vertical')
        
        self.templates_listbox = tk.Listbox(list_frame,
                                            yscrollcommand=scroll_y.set,
                                            font=('Segoe UI', 10))
        
        scroll_y.config(command=self.templates_listbox.yview)
        
        self.templates_listbox.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Add templates
        for template_name in self.TEMPLATES.keys():
            self.templates_listbox.insert('end', template_name)
        
        # Bind selection
        self.templates_listbox.bind('<<ListboxSelect>>', self._on_template_select)
        
        # Description frame
        desc_frame = ttk.LabelFrame(self.templates_tab, text="Opis szablonu", padding="10")
        desc_frame.pack(fill='x', pady=(10, 0))
        
        self.template_desc_label = ttk.Label(desc_frame, text="",
                                            font=('Segoe UI', 9))
        self.template_desc_label.pack()
        
    def _on_recent_select(self, event):
        """Handle recent file selection."""
        selection = self.recent_listbox.curselection()
        if not selection or not self.recent_files:
            return
        
        index = selection[0]
        if index < len(self.recent_files):
            filepath = self.recent_files[index]
            self._load_file(filepath)
            
    def _browse_file(self):
        """Browse for a cost estimate file."""
        filepath = filedialog.askopenfilename(
            title="Wybierz plik kosztorysu",
            filetypes=[("Kosztorys", "*.cost.json"), ("JSON", "*.json"), ("Wszystkie", "*.*")]
        )
        
        if filepath:
            self.file_path_var.set(filepath)
            self._load_file(filepath)
            
    def _load_file(self, filepath: str):
        """Load and preview a cost estimate file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.selected_data = data
            
            # Update preview
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', 'end')
            
            preview = f"Plik: {os.path.basename(filepath)}\n"
            preview += f"Ścieżka: {filepath}\n\n"
            preview += f"Klient: {data.get('client', 'Brak')}\n"
            preview += f"Numer: {data.get('invoice_number', 'Brak')}\n"
            preview += f"Data: {data.get('invoice_date', 'Brak')}\n"
            preview += f"Nazwa: {data.get('quote_name', 'Brak')}\n"
            preview += f"Liczba pozycji: {len(data.get('items', []))}\n"
            preview += f"Transport: {data.get('transport_percent', 0)}%\n"
            
            # Calculate total
            items = data.get('items', [])
            total = sum(item.get('total_gross', 0) for item in items)
            preview += f"Wartość pozycji brutto: {total:.2f} zł\n"
            
            self.preview_text.insert('1.0', preview)
            self.preview_text.config(state='disabled')
            
            # Set name suggestion
            if not self.name_var.get():
                self.name_var.set(data.get('quote_name', 'Nowy kosztorys'))
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{e}")
            self.selected_data = None
            
    def _on_template_select(self, event):
        """Handle template selection."""
        selection = self.templates_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        template_name = self.templates_listbox.get(index)
        template = self.TEMPLATES.get(template_name)
        
        if template:
            self.selected_data = {
                'items': template['items'].copy(),
                'transport_percent': 3.0,
                'transport_vat': 23,
                'client': '',
                'quote_name': template_name,
                'comment': template['description']
            }
            
            # Update description
            desc = f"{template['description']}\n"
            desc += f"Liczba pozycji: {len(template['items'])}"
            self.template_desc_label.config(text=desc)
            
            # Set name suggestion
            if not self.name_var.get():
                self.name_var.set(template_name)
                
    def _create_estimate(self):
        """Create the new estimate based on selection and options."""
        if not self.selected_data:
            messagebox.showwarning("Brak wyboru", 
                                  "Wybierz plik lub szablon do utworzenia kosztorysu.")
            return
        
        if not self.on_create:
            messagebox.showerror("Błąd", "Nie skonfigurowano funkcji tworzenia.")
            return
        
        # Prepare new estimate data
        new_data = {}
        
        # Copy items if selected
        if self.copy_items.get():
            items = self.selected_data.get('items', []).copy()
            
            # Zero quantities if selected
            if self.zero_quantities.get():
                for item in items:
                    item['quantity'] = 0.0
                    item['total_net'] = 0.0
                    item['vat_value'] = 0.0
                    item['total_gross'] = 0.0
            
            new_data['items'] = items
        else:
            new_data['items'] = []
        
        # Copy client if selected
        if self.copy_client.get():
            new_data['client'] = self.selected_data.get('client', '')
        
        # Copy settings if selected
        if self.copy_settings.get():
            new_data['transport_percent'] = self.selected_data.get('transport_percent', 3.0)
            new_data['transport_vat'] = self.selected_data.get('transport_vat', 23)
        
        # Set new name
        new_data['quote_name'] = self.name_var.get() or "Nowy kosztorys"
        
        # Add comment about source
        comment = self.selected_data.get('comment', '')
        if comment:
            new_data['comment'] = f"{comment}\n\n[Utworzono z istniejącego kosztorysu]"
        else:
            new_data['comment'] = "[Utworzono z istniejącego kosztorysu]"
        
        # Call callback
        self.on_create(new_data)
        self.destroy()
