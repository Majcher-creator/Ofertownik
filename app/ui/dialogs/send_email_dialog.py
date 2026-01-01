"""Dialog for sending cost estimate via email."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import tempfile
import os

class SendEmailDialog:
    """Dialog for composing and sending email with cost estimate."""
    
    def __init__(self, parent, email_service, client: Optional[Dict] = None,
                 pdf_generator_callback=None, quote_name: str = ""):
        self.parent = parent
        self.email_service = email_service
        self.client = client
        self.pdf_generator = pdf_generator_callback
        self.quote_name = quote_name
        self.temp_pdf_path: Optional[str] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📧 Wyślij kosztorys emailem")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._prefill_data()
        
        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Cleanup on close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        main = ttk.Frame(self.dialog, padding=15)
        main.pack(fill='both', expand=True)
        
        # To
        ttk.Label(main, text="Do:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        self.to_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.to_var, width=50).grid(
            row=0, column=1, sticky='ew', pady=5)
        
        # CC
        ttk.Label(main, text="CC:").grid(row=1, column=0, sticky='w', pady=5)
        self.cc_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.cc_var, width=50).grid(
            row=1, column=1, sticky='ew', pady=5)
        
        # Subject
        ttk.Label(main, text="Temat:", font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5)
        self.subject_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.subject_var, width=50).grid(
            row=2, column=1, sticky='ew', pady=5)
        
        # Body
        ttk.Label(main, text="Treść:", font=('Segoe UI', 10, 'bold')).grid(
            row=3, column=0, sticky='nw', pady=5)
        
        body_frame = ttk.Frame(main)
        body_frame.grid(row=3, column=1, sticky='nsew', pady=5)
        
        self.body_text = tk.Text(body_frame, height=12, width=50, wrap='word',
                                 font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(body_frame, orient='vertical', command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=scrollbar.set)
        
        self.body_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Attachment info
        self.attach_label = ttk.Label(main, text="📎 Załącznik: kosztorys.pdf (zostanie wygenerowany)",
                                      foreground='gray')
        self.attach_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="⚙️ Ustawienia email",
                  command=self._open_config).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📤 Wyślij", style='Accent.TButton',
                  command=self._send).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Anuluj", command=self._on_close).pack(side='left', padx=5)
        
        main.columnconfigure(1, weight=1)
        main.rowconfigure(3, weight=1)
    
    def _prefill_data(self):
        # Prefill client email
        if self.client and self.client.get('email'):
            self.to_var.set(self.client['email'])
        
        # Prefill subject
        client_name = self.client.get('name', '') if self.client else ''
        subject = f"Kosztorys ofertowy"
        if self.quote_name:
            subject += f" - {self.quote_name}"
        if client_name:
            subject += f" dla {client_name}"
        self.subject_var.set(subject)
        
        # Prefill body
        sender_name = self.email_service.sender_name or "Wykonawca"
        body = f"""Szanowni Państwo,

W załączeniu przesyłam kosztorys ofertowy{' - ' + self.quote_name if self.quote_name else ''}.

Kosztorys jest ważny przez 30 dni od daty wystawienia.

W razie pytań pozostaję do dyspozycji.

Z poważaniem,
{sender_name}
"""
        self.body_text.insert('1.0', body)
    
    def _open_config(self):
        from app.ui.dialogs.email_config_dialog import EmailConfigDialog
        EmailConfigDialog(self.dialog, self.email_service)
    
    def _send(self):
        if not self.to_var.get():
            messagebox.showwarning("Brak odbiorcy", "Wprowadź adres email odbiorcy",
                                  parent=self.dialog)
            return
        
        if not self.email_service.sender_email:
            messagebox.showwarning("Brak konfiguracji",
                                  "Najpierw skonfiguruj ustawienia email.",
                                  parent=self.dialog)
            self._open_config()
            return
        
        # Generate PDF to temp file
        if self.pdf_generator:
            try:
                # Use NamedTemporaryFile for secure temporary file creation
                import tempfile
                temp_fd, self.temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
                os.close(temp_fd)  # Close the file descriptor, we'll use the path
                if not self.pdf_generator(self.temp_pdf_path):
                    messagebox.showerror("Błąd", "Nie udało się wygenerować PDF",
                                        parent=self.dialog)
                    return
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd generowania PDF: {e}",
                                    parent=self.dialog)
                return
        
        # Send email
        result = self.email_service.send_email(
            to_email=self.to_var.get(),
            subject=self.subject_var.get(),
            body=self.body_text.get('1.0', 'end').strip(),
            attachment_path=self.temp_pdf_path,
            cc=self.cc_var.get() if self.cc_var.get() else None
        )
        
        if result['success']:
            messagebox.showinfo("Sukces", "✅ " + result['message'], parent=self.dialog)
            self._on_close()
        else:
            messagebox.showerror("Błąd", "❌ " + result['message'], parent=self.dialog)
    
    def _on_close(self):
        # Cleanup temp file
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try:
                os.remove(self.temp_pdf_path)
            except OSError:
                pass  # Silently ignore file removal errors
        self.dialog.destroy()
