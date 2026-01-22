"""
Dialog windows for the Ofertownik application.
Contains custom dialog classes for client, cost item, and material editing.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from typing import Optional, Dict, Any
from app.utils.formatting import is_valid_float_text


class ClientDialog(simpledialog.Dialog):
    """
    Dialog for creating or editing client information.
    """
    
    def __init__(self, parent, title: str, client: Optional[Dict[str, Any]] = None):
        """
        Initialize the client dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            client: Existing client data to edit (None for new client)
        """
        self.client = client or {}
        super().__init__(parent, title)
    
    def body(self, master):
        """Create dialog body with input fields."""
        ttk.Label(master, text="Nazwa klienta:").grid(row=0, column=0, sticky="w")
        self.e_name = ttk.Entry(master, width=60)
        self.e_name.grid(row=0, column=1, pady=2)
        
        ttk.Label(master, text="Adres:").grid(row=1, column=0, sticky="w")
        self.e_address = ttk.Entry(master, width=60)
        self.e_address.grid(row=1, column=1, pady=2)
        
        ttk.Label(master, text="NIP / ID:").grid(row=2, column=0, sticky="w")
        self.e_id = ttk.Entry(master, width=60)
        self.e_id.grid(row=2, column=1, pady=2)
        
        ttk.Label(master, text="Telefon:").grid(row=3, column=0, sticky="w")
        self.e_phone = ttk.Entry(master, width=60)
        self.e_phone.grid(row=3, column=1, pady=2)
        
        ttk.Label(master, text="E-mail:").grid(row=4, column=0, sticky="w")
        self.e_mail = ttk.Entry(master, width=60)
        self.e_mail.grid(row=4, column=1, pady=2)
        
        # Fill in existing data if editing
        if self.client:
            self.e_name.insert(0, self.client.get("name", ""))
            self.e_address.insert(0, self.client.get("address", ""))
            self.e_id.insert(0, self.client.get("id", ""))
            self.e_phone.insert(0, self.client.get("phone", ""))
            self.e_mail.insert(0, self.client.get("email", ""))
        
        return self.e_name  # Initial focus
    
    def apply(self):
        """Called when OK is pressed - save the result."""
        self.result = {
            "name": self.e_name.get().strip(),
            "address": self.e_address.get().strip(),
            "id": self.e_id.get().strip(),
            "phone": self.e_phone.get().strip(),
            "email": self.e_mail.get().strip()
        }


class CostItemEditDialog(simpledialog.Dialog):
    """
    Dialog for creating or editing a cost item.
    """
    
    def __init__(self, parent, title: str, item: Optional[Dict[str, Any]] = None):
        """
        Initialize the cost item dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            item: Existing item data to edit (None for new item)
        """
        self.item = item or {}
        super().__init__(parent, title)
    
    def body(self, master):
        """Create dialog body with input fields."""
        ttk.Label(master, text="Nazwa:").grid(row=0, column=0, sticky="w")
        self.e_name = ttk.Entry(master, width=50)
        self.e_name.grid(row=0, column=1, pady=2)
        
        ttk.Label(master, text="Ilość:").grid(row=1, column=0, sticky="w")
        self.e_qty = ttk.Entry(master, width=12)
        self.e_qty.grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(master, text="JM:").grid(row=2, column=0, sticky="w")
        self.e_unit = ttk.Entry(master, width=12)
        self.e_unit.grid(row=2, column=1, sticky="w", pady=2)
        
        ttk.Label(master, text="Cena netto:").grid(row=3, column=0, sticky="w")
        self.e_price = ttk.Entry(master, width=12)
        self.e_price.grid(row=3, column=1, sticky="w", pady=2)
        
        ttk.Label(master, text="VAT [%]:").grid(row=4, column=0, sticky="w")
        self.vat_cb = ttk.Combobox(master, values=["0", "8", "23"], width=8, state="readonly")
        self.vat_cb.grid(row=4, column=1, sticky="w")
        
        ttk.Label(master, text="Kategoria:").grid(row=5, column=0, sticky="w")
        self.cat_cb = ttk.Combobox(master, values=["material", "service"], width=12, state="readonly")
        self.cat_cb.grid(row=5, column=1, sticky="w")
        
        ttk.Label(master, text="Notatka:").grid(row=6, column=0, sticky="nw")
        self.t_note = tk.Text(master, height=4, width=40)
        self.t_note.grid(row=6, column=1, pady=2)
        
        # Add validation for numeric fields
        vcmd = (master.register(lambda P: is_valid_float_text(P)), "%P")
        self.e_qty.config(validate="key", validatecommand=vcmd)
        self.e_price.config(validate="key", validatecommand=vcmd)
        
        # Fill in existing data if editing
        if self.item:
            self.e_name.insert(0, self.item.get("name", ""))
            self.e_qty.insert(0, f"{float(self.item.get('quantity', 0.0)):.3f}")
            self.e_unit.insert(0, self.item.get("unit", ""))
            self.e_price.insert(0, f"{float(self.item.get('price_unit_net', 0.0)):.2f}")
            self.vat_cb.set(str(self.item.get("vat_rate", 23)))
            self.cat_cb.set(self.item.get("category", "material"))
            self.t_note.insert("1.0", self.item.get("note", ""))
        else:
            self.vat_cb.set("23")
            self.cat_cb.set("material")
        
        return self.e_name  # Initial focus
    
    def validate(self) -> bool:
        """Validate input before accepting."""
        if not self.e_name.get().strip():
            messagebox.showerror("Błąd", "Nazwa wymagana")
            return False
        
        try:
            float(self.e_qty.get().replace(",", ".") or 0.0)
            float(self.e_price.get().replace(",", ".") or 0.0)
        except ValueError:
            messagebox.showerror("Błąd", "Ilość i cena muszą być liczbami")
            return False
        
        return True
    
    def apply(self):
        """Called when OK is pressed - save the result."""
        self.result = {
            "name": self.e_name.get().strip(),
            "quantity": float(self.e_qty.get().replace(",", ".") or 0.0),
            "unit": self.e_unit.get().strip(),
            "price_unit_net": float(self.e_price.get().replace(",", ".") or 0.0),
            "vat_rate": int(self.vat_cb.get() or 23),
            "category": self.cat_cb.get() or "material",
            "note": self.t_note.get("1.0", "end").strip()
        }


class MaterialEditDialog(simpledialog.Dialog):
    """
    Dialog for creating or editing a material/service in the database.
    """
    
    def __init__(self, parent, title: str, material: Optional[Dict[str, Any]] = None):
        """
        Initialize the material dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            material: Existing material data to edit (None for new material)
        """
        self.material = material or {}
        super().__init__(parent, title)
    
    def body(self, master):
        """Create dialog body with input fields."""
        ttk.Label(master, text="Nazwa:").grid(row=0, column=0, sticky="w")
        self.e_name = ttk.Entry(master, width=60)
        self.e_name.grid(row=0, column=1, pady=2)
        
        ttk.Label(master, text="JM:").grid(row=1, column=0, sticky="w")
        self.e_unit = ttk.Entry(master, width=20)
        self.e_unit.grid(row=1, column=1, pady=2, sticky="w")
        
        ttk.Label(master, text="Cena netto (jedn.):").grid(row=2, column=0, sticky="w")
        self.e_price = ttk.Entry(master, width=20)
        self.e_price.grid(row=2, column=1, pady=2, sticky="w")
        
        ttk.Label(master, text="VAT [%]:").grid(row=3, column=0, sticky="w")
        self.vat_cb = ttk.Combobox(master, values=["0", "8", "23"], width=8, state="readonly")
        self.vat_cb.grid(row=3, column=1, sticky="w")
        
        ttk.Label(master, text="Kategoria:").grid(row=4, column=0, sticky="w")
        self.cat_cb = ttk.Combobox(master, values=["material", "service"], width=12, state="readonly")
        self.cat_cb.grid(row=4, column=1, sticky="w")
        
        # Add validation for price field
        vcmd = (master.register(lambda P: is_valid_float_text(P)), "%P")
        self.e_price.config(validate="key", validatecommand=vcmd)
        
        # Fill in existing data if editing
        if self.material:
            self.e_name.insert(0, self.material.get("name", ""))
            self.e_unit.insert(0, self.material.get("unit", ""))
            self.e_price.insert(0, f"{float(self.material.get('price_unit_net', 0.0)):.2f}")
            self.vat_cb.set(str(self.material.get("vat_rate", 23)))
            self.cat_cb.set(self.material.get("category", "material"))
        else:
            self.vat_cb.set("23")
            self.cat_cb.set("material")
        
        return self.e_name  # Initial focus
    
    def validate(self) -> bool:
        """Validate input before accepting."""
        if not self.e_name.get().strip():
            messagebox.showerror("Błąd", "Nazwa wymagana")
            return False
        
        try:
            float(self.e_price.get().replace(",", ".") or 0.0)
        except ValueError:
            messagebox.showerror("Błąd", "Cena musi być liczbą")
            return False
        
        return True
    
    def apply(self):
        """Called when OK is pressed - save the result."""
        self.result = {
            "name": self.e_name.get().strip(),
            "unit": self.e_unit.get().strip(),
            "price_unit_net": float(self.e_price.get().replace(",", ".") or 0.0),
            "vat_rate": int(self.vat_cb.get() or 23),
            "category": self.cat_cb.get() or "material"
        }


class CompanyEditDialog(simpledialog.Dialog):
    """
    Dialog for editing company information.
    """
    
    def __init__(self, parent, title: str, profile: Optional[Dict[str, Any]] = None):
        """
        Initialize the company edit dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            profile: Existing profile data to edit (None for new profile)
        """
        self.profile = profile or {}
        super().__init__(parent, title)
    
    def body(self, master):
        """Create dialog body with input fields."""
        ttk.Label(master, text="Nazwa firmy:").grid(row=0, column=0, sticky="w", pady=2)
        self.e_company_name = ttk.Entry(master, width=60)
        self.e_company_name.grid(row=0, column=1, pady=2)
        
        ttk.Label(master, text="Adres:").grid(row=1, column=0, sticky="w", pady=2)
        self.e_company_address = ttk.Entry(master, width=60)
        self.e_company_address.grid(row=1, column=1, pady=2)
        
        ttk.Label(master, text="NIP:").grid(row=2, column=0, sticky="w", pady=2)
        self.e_company_nip = ttk.Entry(master, width=60)
        self.e_company_nip.grid(row=2, column=1, pady=2)
        
        ttk.Label(master, text="Telefon:").grid(row=3, column=0, sticky="w", pady=2)
        self.e_company_phone = ttk.Entry(master, width=60)
        self.e_company_phone.grid(row=3, column=1, pady=2)
        
        ttk.Label(master, text="E-mail:").grid(row=4, column=0, sticky="w", pady=2)
        self.e_company_email = ttk.Entry(master, width=60)
        self.e_company_email.grid(row=4, column=1, pady=2)
        
        ttk.Label(master, text="Numer konta:").grid(row=5, column=0, sticky="w", pady=2)
        self.e_company_account = ttk.Entry(master, width=60)
        self.e_company_account.grid(row=5, column=1, pady=2)
        
        # Fill in existing data if editing
        if self.profile:
            self.e_company_name.insert(0, self.profile.get("company_name", ""))
            self.e_company_address.insert(0, self.profile.get("company_address", ""))
            self.e_company_nip.insert(0, self.profile.get("company_nip", ""))
            self.e_company_phone.insert(0, self.profile.get("company_phone", ""))
            self.e_company_email.insert(0, self.profile.get("company_email", ""))
            self.e_company_account.insert(0, self.profile.get("company_account", ""))
        
        return self.e_company_name  # Initial focus
    
    def apply(self):
        """Called when OK is pressed - save the result."""
        self.result = {
            "company_name": self.e_company_name.get().strip(),
            "company_address": self.e_company_address.get().strip(),
            "company_nip": self.e_company_nip.get().strip(),
            "company_phone": self.e_company_phone.get().strip(),
            "company_email": self.e_company_email.get().strip(),
            "company_account": self.e_company_account.get().strip(),
            "logo": self.profile.get("logo", "")  # Preserve existing logo
        }
