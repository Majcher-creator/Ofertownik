"""
Dialog for managing margin settings in cost estimates.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict

from app.services.margin_calculator import MarginSettings


class MarginSettingsDialog(tk.Toplevel):
    """
    Dialog for configuring margin settings.
    Allows setting global margin and per-group margins.
    """
    
    def __init__(self, parent, settings: MarginSettings, groups: list,
                 on_save: Optional[Callable[[MarginSettings], None]] = None):
        """
        Initialize the margin settings dialog.
        
        Args:
            parent: Parent window
            settings: Current MarginSettings
            groups: List of available groups
            on_save: Callback function when settings are saved
        """
        super().__init__(parent)
        self.title("Ustawienia marży")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.settings = settings
        self.groups = groups
        self.on_save = on_save
        self.result = None
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Make modal
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Konfiguracja marży", 
                               font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Global margin section
        global_frame = ttk.LabelFrame(main_frame, text="Marża globalna", padding="10")
        global_frame.pack(fill=tk.X, pady=(0, 10))
        
        global_inner = ttk.Frame(global_frame)
        global_inner.pack(fill=tk.X)
        
        ttk.Label(global_inner, text="Marża globalna (%):").pack(side=tk.LEFT)
        self.global_margin_var = tk.StringVar(value=str(self.settings.global_margin_percent))
        global_entry = ttk.Entry(global_inner, textvariable=self.global_margin_var, width=10)
        global_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(global_inner, text="(domyślna dla wszystkich pozycji)", 
                 foreground="#7F8C8D").pack(side=tk.LEFT, padx=5)
        
        # Group margins section
        group_frame = ttk.LabelFrame(main_frame, text="Marże dla grup", padding="10")
        group_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Instructions
        ttk.Label(group_frame, text="Ustaw niestandardowe marże dla poszczególnych grup:",
                 foreground="#7F8C8D").pack(pady=(0, 10))
        
        # Scrollable frame for group margins
        canvas_frame = ttk.Frame(group_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, height=150)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Group margin entries
        self.group_margin_vars: Dict[str, tk.StringVar] = {}
        
        if self.groups:
            for group in self.groups:
                group_row = ttk.Frame(scrollable_frame)
                group_row.pack(fill=tk.X, pady=2)
                
                ttk.Label(group_row, text=f"{group}:", width=20).pack(side=tk.LEFT)
                
                var = tk.StringVar()
                if group in self.settings.group_margins:
                    var.set(str(self.settings.group_margins[group]))
                else:
                    var.set("")
                
                self.group_margin_vars[group] = var
                
                entry = ttk.Entry(group_row, textvariable=var, width=10)
                entry.pack(side=tk.LEFT, padx=5)
                
                ttk.Label(group_row, text="%").pack(side=tk.LEFT)
                
                # Clear button
                clear_btn = ttk.Button(group_row, text="Wyczyść", width=8,
                                      command=lambda v=var: v.set(""))
                clear_btn.pack(side=tk.LEFT, padx=5)
        else:
            ttk.Label(scrollable_frame, text="Brak grup do skonfigurowania",
                     foreground="#7F8C8D").pack(pady=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Zapisz", command=self._on_save,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Anuluj", command=self._on_cancel).pack(side=tk.RIGHT)
        
        # Help text
        help_text = ("💡 Priorytet marży: pozycja > grupa > globalna\n"
                    "Pozostaw pole grupy puste, aby używać marży globalnej.")
        help_label = ttk.Label(main_frame, text=help_text, foreground="#7F8C8D",
                              font=('Segoe UI', 8))
        help_label.pack(pady=(10, 0))
    
    def _on_save(self):
        """Save margin settings."""
        try:
            # Validate and save global margin
            global_margin = float(self.global_margin_var.get())
            if global_margin < 0:
                messagebox.showerror("Błąd", "Marża globalna nie może być ujemna.")
                return
            
            # Create new settings
            new_settings = MarginSettings(global_margin_percent=global_margin)
            
            # Validate and save group margins
            for group, var in self.group_margin_vars.items():
                value = var.get().strip()
                if value:
                    try:
                        margin = float(value)
                        if margin < 0:
                            messagebox.showerror("Błąd", 
                                f"Marża dla grupy '{group}' nie może być ujemna.")
                            return
                        new_settings.set_group_margin(group, margin)
                    except ValueError:
                        messagebox.showerror("Błąd", 
                            f"Nieprawidłowa wartość marży dla grupy '{group}'.")
                        return
            
            self.result = new_settings
            
            if self.on_save:
                self.on_save(new_settings)
            
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowa wartość marży globalnej.")
    
    def _on_cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.destroy()
    
    def show(self) -> Optional[MarginSettings]:
        """
        Show dialog and wait for result.
        
        Returns:
            Updated MarginSettings or None if cancelled
        """
        self.wait_window()
        return self.result
