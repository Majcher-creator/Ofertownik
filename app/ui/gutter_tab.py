"""
Enhanced gutter tab for the main application.
Provides UI for managing gutter systems with different types and accessories.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Dict, Any
import os

from app.models.gutter_models import GutterSystem, GutterAccessory, GutterTemplate
from app.services.gutter_service import GutterSystemManager


class GutterAccessoriesDialog(tk.Toplevel):
    """Dialog for reviewing and editing gutter accessories before adding to cost estimate."""
    
    def __init__(self, parent, accessories: List[GutterAccessory], title: str = "Przegląd akcesoriów rynnowych"):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent window
            accessories: List of accessories to display and edit
            title: Dialog title
        """
        super().__init__(parent)
        self.title(title)
        self.accessories = accessories
        self.result = None
        self.selected_items = []
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Size and position
        self.geometry("900x500")
        self._center_window()
        
        self._create_widgets()
        
        # Wait for dialog to close
        self.wait_window()
    
    def _center_window(self):
        """Center the dialog on parent window."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Instructions
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            info_frame,
            text="Przegląd i edycja akcesoriów rynnowych. Zaznacz pozycje do dodania do kosztorysu.",
            wraplength=850
        ).pack()
        
        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        columns = ("select", "name", "quantity", "unit", "price", "total")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="extended"
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Column headings
        self.tree.heading("select", text="✓")
        self.tree.heading("name", text="Nazwa")
        self.tree.heading("quantity", text="Ilość")
        self.tree.heading("unit", text="JM")
        self.tree.heading("price", text="Cena jedn. netto")
        self.tree.heading("total", text="Wartość netto")
        
        # Column widths
        self.tree.column("select", width=40, anchor="center")
        self.tree.column("name", width=300)
        self.tree.column("quantity", width=100, anchor="center")
        self.tree.column("unit", width=80, anchor="center")
        self.tree.column("price", width=120, anchor="e")
        self.tree.column("total", width=120, anchor="e")
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Populate tree
        self.checkboxes = {}
        for idx, acc in enumerate(self.accessories):
            if acc.quantity > 0:  # Only show items with quantity > 0
                total = acc.quantity * acc.price_unit_net
                item_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        "✓",
                        acc.name,
                        f"{acc.quantity:.2f}",
                        acc.unit,
                        f"{acc.price_unit_net:.2f} zł",
                        f"{total:.2f} zł"
                    ),
                    tags=(str(idx),)
                )
                self.checkboxes[item_id] = True
        
        # Select all items by default
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        
        # Bind double-click to edit
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Button-1>", self._on_click)
        
        # Action buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Edytuj wybraną", command=self._edit_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zaznacz wszystkie", command=self._select_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odznacz wszystkie", command=self._deselect_all).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Anuluj", command=self._cancel).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Dodaj do kosztorysu", command=self._ok).pack(side="right", padx=5)
    
    def _on_click(self, event):
        """Handle click on tree item."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Checkbox column
                item = self.tree.identify_row(event.y)
                if item:
                    # Toggle selection
                    if item in self.tree.selection():
                        self.tree.selection_remove(item)
                        # Update checkmark
                        values = list(self.tree.item(item, "values"))
                        values[0] = ""
                        self.tree.item(item, values=values)
                    else:
                        self.tree.selection_add(item)
                        # Update checkmark
                        values = list(self.tree.item(item, "values"))
                        values[0] = "✓"
                        self.tree.item(item, values=values)
    
    def _on_double_click(self, event):
        """Handle double-click to edit item."""
        self._edit_selected()
    
    def _edit_selected(self):
        """Edit the selected accessory."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Wybór", "Wybierz akcesorium do edycji.")
            return
        
        if len(selection) > 1:
            messagebox.showinfo("Wybór", "Wybierz tylko jedno akcesorium do edycji.")
            return
        
        item_id = selection[0]
        tags = self.tree.item(item_id, "tags")
        if not tags:
            return
        
        idx = int(tags[0])
        acc = self.accessories[idx]
        
        # Create edit dialog
        dialog = GutterAccessoryEditDialog(self, acc)
        if dialog.result:
            # Update accessory
            acc.quantity = dialog.result['quantity']
            acc.price_unit_net = dialog.result['price']
            
            # Update tree
            total = acc.quantity * acc.price_unit_net
            values = list(self.tree.item(item_id, "values"))
            values[2] = f"{acc.quantity:.2f}"
            values[4] = f"{acc.price_unit_net:.2f} zł"
            values[5] = f"{total:.2f} zł"
            self.tree.item(item_id, values=values)
    
    def _select_all(self):
        """Select all items."""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
            values = list(self.tree.item(item, "values"))
            values[0] = "✓"
            self.tree.item(item, values=values)
    
    def _deselect_all(self):
        """Deselect all items."""
        for item in self.tree.get_children():
            self.tree.selection_remove(item)
            values = list(self.tree.item(item, "values"))
            values[0] = ""
            self.tree.item(item, values=values)
    
    def _ok(self):
        """Save selected items and close."""
        selection = self.tree.selection()
        if not selection:
            if messagebox.askyesno("Brak wyboru", "Nie wybrano żadnych akcesoriów. Zamknąć bez dodawania?"):
                self.result = []
                self.destroy()
            return
        
        # Get selected accessories
        self.result = []
        for item_id in selection:
            tags = self.tree.item(item_id, "tags")
            if tags:
                idx = int(tags[0])
                self.result.append(self.accessories[idx])
        
        self.destroy()
    
    def _cancel(self):
        """Cancel and close."""
        self.result = None
        self.destroy()


class GutterAccessoryEditDialog(simpledialog.Dialog):
    """Simple dialog for editing accessory quantity and price."""
    
    def __init__(self, parent, accessory: GutterAccessory):
        self.accessory = accessory
        self.result = None
        super().__init__(parent, f"Edycja: {accessory.name}")
    
    def body(self, master):
        """Create dialog body."""
        ttk.Label(master, text="Ilość:").grid(row=0, column=0, sticky="w", pady=5)
        self.e_quantity = ttk.Entry(master, width=15)
        self.e_quantity.grid(row=0, column=1, pady=5, padx=5)
        self.e_quantity.insert(0, str(self.accessory.quantity))
        
        ttk.Label(master, text="Cena jednostkowa netto:").grid(row=1, column=0, sticky="w", pady=5)
        self.e_price = ttk.Entry(master, width=15)
        self.e_price.grid(row=1, column=1, pady=5, padx=5)
        self.e_price.insert(0, str(self.accessory.price_unit_net))
        
        return self.e_quantity
    
    def validate(self):
        """Validate input."""
        try:
            quantity = float(self.e_quantity.get())
            price = float(self.e_price.get())
            if quantity < 0 or price < 0:
                messagebox.showerror("Błąd", "Wartości nie mogą być ujemne.")
                return False
            return True
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe wartości liczbowe.")
            return False
    
    def apply(self):
        """Save values."""
        self.result = {
            'quantity': float(self.e_quantity.get()),
            'price': float(self.e_price.get())
        }


class SaveTemplateDialog(simpledialog.Dialog):
    """Dialog for saving a gutter system template."""
    
    def __init__(self, parent):
        self.result = None
        super().__init__(parent, "Zapisz szablon")
    
    def body(self, master):
        """Create dialog body."""
        ttk.Label(master, text="Nazwa szablonu:").grid(row=0, column=0, sticky="w", pady=5)
        self.e_name = ttk.Entry(master, width=40)
        self.e_name.grid(row=0, column=1, pady=5, padx=5)
        
        return self.e_name
    
    def validate(self):
        """Validate input."""
        name = self.e_name.get().strip()
        if not name:
            messagebox.showerror("Błąd", "Podaj nazwę szablonu.")
            return False
        return True
    
    def apply(self):
        """Save value."""
        self.result = self.e_name.get().strip()
