"""Dialog for configuring email settings."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

class EmailConfigDialog:
    """Dialog for SMTP email configuration."""
    
    def __init__(self, parent, email_service, on_save: Optional[Callable] = None):
        self.parent = parent
        self.email_service = email_service
        self.on_save = on_save
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Konfiguracja Email")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._load_current_settings()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        main = ttk.Frame(self.dialog, padding=20)
        main.pack(fill='both', expand=True)
        
        # Provider selection
        ttk.Label(main, text="Dostawca email:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=(0, 5))
        
        self.provider_var = tk.StringVar(value='Gmail')
        provider_cb = ttk.Combobox(main, textvariable=self.provider_var,
                                   values=list(self.email_service.PROVIDERS.keys()),
                                   state='readonly', width=30)
        provider_cb.grid(row=0, column=1, sticky='ew', pady=(0, 5))
        provider_cb.bind('<<ComboboxSelected>>', self._on_provider_change)
        
        # SMTP Server
        ttk.Label(main, text="Serwer SMTP:").grid(row=1, column=0, sticky='w', pady=5)
        self.server_var = tk.StringVar()
        self.server_entry = ttk.Entry(main, textvariable=self.server_var, width=35)
        self.server_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Port
        ttk.Label(main, text="Port:").grid(row=2, column=0, sticky='w', pady=5)
        self.port_var = tk.IntVar(value=587)
        port_entry = ttk.Entry(main, textvariable=self.port_var, width=10)
        port_entry.grid(row=2, column=1, sticky='w', pady=5)
        
        # TLS
        self.tls_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main, text="Użyj TLS", variable=self.tls_var).grid(
            row=3, column=1, sticky='w', pady=5)
        
        ttk.Separator(main, orient='horizontal').grid(
            row=4, column=0, columnspan=2, sticky='ew', pady=15)
        
        # Sender email
        ttk.Label(main, text="Twój email:", font=('Segoe UI', 10, 'bold')).grid(
            row=5, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.email_var, width=35).grid(
            row=5, column=1, sticky='ew', pady=5)
        
        # Sender name
        ttk.Label(main, text="Nazwa nadawcy:").grid(row=6, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.name_var, width=35).grid(
            row=6, column=1, sticky='ew', pady=5)
        
        # Password
        ttk.Label(main, text="Hasło/App Password:").grid(row=7, column=0, sticky='w', pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.password_var, show='*', width=35).grid(
            row=7, column=1, sticky='ew', pady=5)
        
        # Note label
        self.note_label = ttk.Label(main, text="", foreground='gray', wraplength=350)
        self.note_label.grid(row=8, column=0, columnspan=2, sticky='w', pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="🔌 Test połączenia", command=self._test_connection).pack(
            side='left', padx=5)
        ttk.Button(btn_frame, text="💾 Zapisz", style='Accent.TButton',
                  command=self._save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Anuluj", command=self.dialog.destroy).pack(
            side='left', padx=5)
        
        main.columnconfigure(1, weight=1)
        
        # Initial provider setup
        self._on_provider_change()
    
    def _on_provider_change(self, event=None):
        provider = self.provider_var.get()
        settings = self.email_service.PROVIDERS.get(provider, {})
        
        if settings.get('smtp_server'):
            self.server_var.set(settings['smtp_server'])
            self.server_entry.configure(state='readonly')
        else:
            self.server_var.set('')
            self.server_entry.configure(state='normal')
        
        self.port_var.set(settings.get('smtp_port', 587))
        self.tls_var.set(settings.get('use_tls', True))
        self.note_label.configure(text=settings.get('note', ''))
    
    def _load_current_settings(self):
        if self.email_service.sender_email:
            self.email_var.set(self.email_service.sender_email)
            self.name_var.set(self.email_service.sender_name)
            self.server_var.set(self.email_service.smtp_server)
            self.port_var.set(self.email_service.smtp_port)
            self.tls_var.set(self.email_service.use_tls)
    
    def _test_connection(self):
        self._apply_settings()
        result = self.email_service.test_connection(self.password_var.get())
        if result['success']:
            messagebox.showinfo("Test", "✅ " + result['message'], parent=self.dialog)
        else:
            messagebox.showerror("Test", "❌ " + result['message'], parent=self.dialog)
    
    def _apply_settings(self):
        self.email_service.configure(
            smtp_server=self.server_var.get(),
            smtp_port=self.port_var.get(),
            sender_email=self.email_var.get(),
            sender_name=self.name_var.get(),
            use_tls=self.tls_var.get()
        )
    
    def _save(self):
        if not self.email_var.get():
            messagebox.showwarning("Brak danych", "Wprowadź adres email", parent=self.dialog)
            return
        
        self._apply_settings()
        
        # Save password if provided
        if self.password_var.get():
            self.email_service.save_password(self.password_var.get())
        
        self.result = True
        if self.on_save:
            self.on_save()
        
        messagebox.showinfo("Zapisano", "Ustawienia email zostały zapisane.", parent=self.dialog)
        self.dialog.destroy()
