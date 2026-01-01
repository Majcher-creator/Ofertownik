"""
History dialog for viewing and managing cost estimate versions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from datetime import datetime

from app.models.history import CostEstimateHistory, HistoryEntry
from app.utils.formatting import fmt_money


class HistoryDialog(tk.Toplevel):
    """
    Dialog for viewing cost estimate history and managing versions.
    """
    
    def __init__(self, parent, history: CostEstimateHistory, 
                 on_restore: Optional[Callable[[HistoryEntry], None]] = None):
        """
        Initialize the history dialog.
        
        Args:
            parent: Parent window
            history: CostEstimateHistory instance
            on_restore: Callback function when restoring a version
        """
        super().__init__(parent)
        self.history = history
        self.on_restore = on_restore
        self.selected_entry: Optional[HistoryEntry] = None
        
        self.title("Historia zmian kosztorysu")
        self.geometry("900x600")
        self.transient(parent)
        
        self._create_ui()
        self._load_history()
        
    def _create_ui(self):
        """Create the dialog UI."""
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                                text="Historia zmian kosztorysu",
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Treeview for history list
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame,
                                 columns=('version', 'date', 'time', 'description', 'items', 'total'),
                                 show='headings',
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading('version', text='Wersja')
        self.tree.heading('date', text='Data')
        self.tree.heading('time', text='Czas')
        self.tree.heading('description', text='Opis')
        self.tree.heading('items', text='Pozycje')
        self.tree.heading('total', text='Wartość brutto')
        
        self.tree.column('version', width=60, anchor='center')
        self.tree.column('date', width=100, anchor='center')
        self.tree.column('time', width=80, anchor='center')
        self.tree.column('description', width=300, anchor='w')
        self.tree.column('items', width=80, anchor='center')
        self.tree.column('total', width=120, anchor='e')
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Details panel
        details_frame = ttk.LabelFrame(main_frame, text="Szczegóły wersji", padding="10")
        details_frame.pack(fill='x', pady=(10, 0))
        
        self.details_text = tk.Text(details_frame, height=6, wrap='word', 
                                    state='disabled', font=('Segoe UI', 10))
        self.details_text.pack(fill='x')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Przywróć", 
                  command=self._restore_version).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Porównaj wersje...", 
                  command=self._compare_versions).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Podgląd pozycji...", 
                  command=self._preview_items).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Zamknij", 
                  command=self.destroy).pack(side='right', padx=5)
        
    def _load_history(self):
        """Load history entries into the treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add entries (newest first)
        entries = self.history.get_all_entries()
        for entry in reversed(entries):
            # Parse timestamp
            try:
                dt = datetime.fromisoformat(entry.timestamp)
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M:%S")
            except:
                date_str = entry.timestamp.split('T')[0] if 'T' in entry.timestamp else ''
                time_str = entry.timestamp.split('T')[1][:8] if 'T' in entry.timestamp else ''
            
            self.tree.insert('', 'end', values=(
                entry.version,
                date_str,
                time_str,
                entry.description,
                entry.items_count,
                fmt_money(entry.total_gross)
            ), tags=(entry.version,))
        
        # Select latest if available
        if entries:
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self.tree.focus(first_item)
    
    def _on_select(self, event):
        """Handle selection change in treeview."""
        selection = self.tree.selection()
        if not selection:
            self.selected_entry = None
            self._update_details(None)
            return
        
        # Get selected version
        item = selection[0]
        version = int(self.tree.item(item)['values'][0])
        self.selected_entry = self.history.get_entry(version)
        self._update_details(self.selected_entry)
    
    def _update_details(self, entry: Optional[HistoryEntry]):
        """Update the details panel with entry information."""
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        
        if entry:
            details = f"Wersja: {entry.version}\n"
            details += f"Data: {entry.timestamp}\n"
            details += f"Opis: {entry.description}\n"
            details += f"Liczba pozycji: {entry.items_count}\n"
            details += f"Wartość brutto: {fmt_money(entry.total_gross)}\n"
            details += f"Checksum: {entry.checksum[:16]}...\n"
            
            # Add metadata if available
            if entry.metadata:
                details += f"\nMetadane:\n"
                for key, value in entry.metadata.items():
                    details += f"  {key}: {value}\n"
            
            self.details_text.insert('1.0', details)
        
        self.details_text.config(state='disabled')
    
    def _restore_version(self):
        """Restore the selected version."""
        if not self.selected_entry:
            messagebox.showwarning("Brak wyboru", 
                                  "Wybierz wersję do przywrócenia.")
            return
        
        if not self.on_restore:
            messagebox.showwarning("Brak funkcji", 
                                  "Nie skonfigurowano funkcji przywracania.")
            return
        
        # Confirm restoration
        msg = f"Czy na pewno przywrócić wersję {self.selected_entry.version}?\n\n"
        msg += f"Opis: {self.selected_entry.description}\n"
        msg += f"Pozycje: {self.selected_entry.items_count}\n"
        msg += f"Wartość: {fmt_money(self.selected_entry.total_gross)}"
        
        if messagebox.askyesno("Potwierdź przywrócenie", msg):
            self.on_restore(self.selected_entry)
            self.destroy()
    
    def _compare_versions(self):
        """Open dialog to compare two versions."""
        if len(self.history.get_all_entries()) < 2:
            messagebox.showinfo("Za mało wersji", 
                               "Potrzebne są co najmniej 2 wersje do porównania.")
            return
        
        # Open compare dialog
        dialog = CompareVersionsDialog(self, self.history)
        self.wait_window(dialog)
    
    def _preview_items(self):
        """Preview items in the selected version."""
        if not self.selected_entry:
            messagebox.showwarning("Brak wyboru", 
                                  "Wybierz wersję do podglądu.")
            return
        
        # Open preview dialog
        dialog = PreviewItemsDialog(self, self.selected_entry)
        self.wait_window(dialog)


class CompareVersionsDialog(tk.Toplevel):
    """
    Dialog for comparing two versions of a cost estimate.
    """
    
    def __init__(self, parent, history: CostEstimateHistory):
        """
        Initialize the compare versions dialog.
        
        Args:
            parent: Parent window
            history: CostEstimateHistory instance
        """
        super().__init__(parent)
        self.history = history
        
        self.title("Porównaj wersje")
        self.geometry("1000x700")
        self.transient(parent)
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the dialog UI."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                                text="Porównanie wersji kosztorysu",
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Version selection frame
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        # Version 1 selector
        ttk.Label(selection_frame, text="Wersja 1:").grid(row=0, column=0, padx=5, sticky='w')
        versions = [str(e.version) for e in self.history.get_all_entries()]
        self.version1_var = tk.StringVar(value=versions[0] if versions else '')
        version1_combo = ttk.Combobox(selection_frame, textvariable=self.version1_var,
                                      values=versions, state='readonly', width=10)
        version1_combo.grid(row=0, column=1, padx=5)
        
        # Version 2 selector
        ttk.Label(selection_frame, text="Wersja 2:").grid(row=0, column=2, padx=5, sticky='w')
        self.version2_var = tk.StringVar(value=versions[-1] if len(versions) > 1 else '')
        version2_combo = ttk.Combobox(selection_frame, textvariable=self.version2_var,
                                      values=versions, state='readonly', width=10)
        version2_combo.grid(row=0, column=3, padx=5)
        
        # Compare button
        ttk.Button(selection_frame, text="Porównaj", 
                  command=self._do_compare).grid(row=0, column=4, padx=10)
        
        # Results notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Added items tab
        self.added_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.added_frame, text="Dodane")
        self._create_items_tree(self.added_frame, 'added')
        
        # Removed items tab
        self.removed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.removed_frame, text="Usunięte")
        self._create_items_tree(self.removed_frame, 'removed')
        
        # Changed items tab
        self.changed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.changed_frame, text="Zmienione")
        self._create_changed_tree(self.changed_frame)
        
        # Close button
        ttk.Button(main_frame, text="Zamknij", 
                  command=self.destroy).pack(pady=(10, 0))
    
    def _create_items_tree(self, parent, tree_name: str):
        """Create a treeview for items (added/removed)."""
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame, orient='vertical')
        scroll_x = ttk.Scrollbar(frame, orient='horizontal')
        
        tree = ttk.Treeview(frame,
                           columns=('name', 'quantity', 'unit', 'price', 'total'),
                           show='headings',
                           yscrollcommand=scroll_y.set,
                           xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        
        tree.heading('name', text='Nazwa')
        tree.heading('quantity', text='Ilość')
        tree.heading('unit', text='JM')
        tree.heading('price', text='Cena jedn.')
        tree.heading('total', text='Wartość brutto')
        
        tree.column('name', width=300, anchor='w')
        tree.column('quantity', width=80, anchor='e')
        tree.column('unit', width=60, anchor='center')
        tree.column('price', width=100, anchor='e')
        tree.column('total', width=120, anchor='e')
        
        tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        setattr(self, f'{tree_name}_tree', tree)
    
    def _create_changed_tree(self, parent):
        """Create a treeview for changed items."""
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame, orient='vertical')
        scroll_x = ttk.Scrollbar(frame, orient='horizontal')
        
        tree = ttk.Treeview(frame,
                           columns=('name', 'field', 'old_value', 'new_value'),
                           show='headings',
                           yscrollcommand=scroll_y.set,
                           xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        
        tree.heading('name', text='Nazwa pozycji')
        tree.heading('field', text='Pole')
        tree.heading('old_value', text='Stara wartość')
        tree.heading('new_value', text='Nowa wartość')
        
        tree.column('name', width=300, anchor='w')
        tree.column('field', width=120, anchor='w')
        tree.column('old_value', width=150, anchor='e')
        tree.column('new_value', width=150, anchor='e')
        
        tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        self.changed_tree = tree
    
    def _do_compare(self):
        """Perform the comparison."""
        try:
            version1 = int(self.version1_var.get())
            version2 = int(self.version2_var.get())
        except (ValueError, AttributeError):
            messagebox.showerror("Błąd", "Wybierz obie wersje do porównania.")
            return
        
        if version1 == version2:
            messagebox.showwarning("Ta sama wersja", 
                                  "Wybierz różne wersje do porównania.")
            return
        
        # Get comparison
        comparison = self.history.compare_versions(version1, version2)
        
        # Clear all trees
        for item in self.added_tree.get_children():
            self.added_tree.delete(item)
        for item in self.removed_tree.get_children():
            self.removed_tree.delete(item)
        for item in self.changed_tree.get_children():
            self.changed_tree.delete(item)
        
        # Populate added items
        for item in comparison['added']:
            self.added_tree.insert('', 'end', values=(
                item.get('name', ''),
                f"{item.get('quantity', 0):.2f}",
                item.get('unit', ''),
                fmt_money(item.get('price_unit_net', 0)),
                fmt_money(item.get('total_gross', 0))
            ))
        
        # Populate removed items
        for item in comparison['removed']:
            self.removed_tree.insert('', 'end', values=(
                item.get('name', ''),
                f"{item.get('quantity', 0):.2f}",
                item.get('unit', ''),
                fmt_money(item.get('price_unit_net', 0)),
                fmt_money(item.get('total_gross', 0))
            ))
        
        # Populate changed items
        for change in comparison['changed']:
            old_item = change['old']
            new_item = change['new']
            name = old_item.get('name', '')
            
            # Check each field for changes
            if old_item.get('quantity') != new_item.get('quantity'):
                self.changed_tree.insert('', 'end', values=(
                    name, 'Ilość',
                    f"{old_item.get('quantity', 0):.2f}",
                    f"{new_item.get('quantity', 0):.2f}"
                ))
            
            if old_item.get('price_unit_net') != new_item.get('price_unit_net'):
                self.changed_tree.insert('', 'end', values=(
                    name, 'Cena jednostkowa',
                    fmt_money(old_item.get('price_unit_net', 0)),
                    fmt_money(new_item.get('price_unit_net', 0))
                ))
            
            if old_item.get('vat_rate') != new_item.get('vat_rate'):
                self.changed_tree.insert('', 'end', values=(
                    name, 'Stawka VAT',
                    f"{old_item.get('vat_rate', 0)}%",
                    f"{new_item.get('vat_rate', 0)}%"
                ))


class PreviewItemsDialog(tk.Toplevel):
    """
    Dialog for previewing items in a historical version.
    """
    
    def __init__(self, parent, entry: HistoryEntry):
        """
        Initialize the preview items dialog.
        
        Args:
            parent: Parent window
            entry: HistoryEntry to preview
        """
        super().__init__(parent)
        self.entry = entry
        
        self.title(f"Podgląd pozycji - Wersja {entry.version}")
        self.geometry("900x600")
        self.transient(parent)
        
        self._create_ui()
        self._load_items()
        
    def _create_ui(self):
        """Create the dialog UI."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = f"Pozycje kosztorysowe - Wersja {self.entry.version}"
        title_label = ttk.Label(main_frame, text=title,
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Opis: {self.entry.description}").pack(side='left', padx=5)
        ttk.Label(info_frame, text=f"Data: {self.entry.timestamp.split('T')[0]}").pack(side='left', padx=5)
        ttk.Label(info_frame, text=f"Wartość: {fmt_money(self.entry.total_gross)}").pack(side='right', padx=5)
        
        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
        scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        self.tree = ttk.Treeview(tree_frame,
                                 columns=('name', 'quantity', 'unit', 'price', 'vat', 'total'),
                                 show='headings',
                                 yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.heading('name', text='Nazwa')
        self.tree.heading('quantity', text='Ilość')
        self.tree.heading('unit', text='JM')
        self.tree.heading('price', text='Cena jedn. netto')
        self.tree.heading('vat', text='VAT')
        self.tree.heading('total', text='Wartość brutto')
        
        self.tree.column('name', width=300, anchor='w')
        self.tree.column('quantity', width=80, anchor='e')
        self.tree.column('unit', width=60, anchor='center')
        self.tree.column('price', width=100, anchor='e')
        self.tree.column('vat', width=60, anchor='center')
        self.tree.column('total', width=120, anchor='e')
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Close button
        ttk.Button(main_frame, text="Zamknij", 
                  command=self.destroy).pack(pady=(10, 0))
    
    def _load_items(self):
        """Load items into the treeview."""
        for item in self.entry.items_snapshot:
            self.tree.insert('', 'end', values=(
                item.get('name', ''),
                f"{item.get('quantity', 0):.2f}",
                item.get('unit', ''),
                fmt_money(item.get('price_unit_net', 0)),
                f"{item.get('vat_rate', 0)}%",
                fmt_money(item.get('total_gross', 0))
            ))
