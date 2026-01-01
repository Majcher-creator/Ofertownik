"""
Email service for sending cost estimates.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class EmailService:
    """Service for sending emails with attachments."""
    
    # Predefiniowane ustawienia dla popularnych dostawców
    PROVIDERS = {
        'Gmail': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True,
            'note': 'Wymaga App Password (nie zwykłe hasło)'
        },
        'Outlook/Hotmail': {
            'smtp_server': 'smtp-mail.outlook.com',
            'smtp_port': 587,
            'use_tls': True,
            'note': ''
        },
        'Office 365': {
            'smtp_server': 'smtp.office365.com',
            'smtp_port': 587,
            'use_tls': True,
            'note': ''
        },
        'Yahoo': {
            'smtp_server': 'smtp.mail.yahoo.com',
            'smtp_port': 587,
            'use_tls': True,
            'note': 'Wymaga App Password'
        },
        'Własny serwer': {
            'smtp_server': '',
            'smtp_port': 587,
            'use_tls': True,
            'note': 'Wprowadź własne ustawienia'
        }
    }
    
    KEYRING_SERVICE = "Ofertownik_Email"
    
    def __init__(self):
        self.smtp_server: str = ""
        self.smtp_port: int = 587
        self.use_tls: bool = True
        self.sender_email: str = ""
        self.sender_name: str = ""
    
    def configure(self, smtp_server: str, smtp_port: int, 
                  sender_email: str, sender_name: str = "",
                  use_tls: bool = True) -> None:
        """Configure email settings."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_name = sender_name or sender_email
        self.use_tls = use_tls
    
    def save_password(self, password: str) -> bool:
        """Save password securely using keyring."""
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.set_password(self.KEYRING_SERVICE, self.sender_email, password)
            return True
        except Exception:
            return False
    
    def get_password(self) -> Optional[str]:
        """Retrieve password from keyring."""
        if not KEYRING_AVAILABLE:
            return None
        try:
            return keyring.get_password(self.KEYRING_SERVICE, self.sender_email)
        except Exception:
            return None
    
    def delete_password(self) -> bool:
        """Delete stored password."""
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.sender_email)
            return True
        except Exception:
            return False
    
    def send_email(self, to_email: str, subject: str, body: str,
                   attachment_path: Optional[str] = None,
                   password: Optional[str] = None,
                   cc: Optional[str] = None,
                   bcc: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email with optional PDF attachment.
        
        Returns:
            Dict with 'success' (bool) and 'message' (str)
        """
        if not self.smtp_server or not self.sender_email:
            return {'success': False, 'message': 'Email nie jest skonfigurowany'}
        
        # Get password
        pwd = password or self.get_password()
        if not pwd:
            return {'success': False, 'message': 'Brak hasła. Skonfiguruj ustawienia email.'}
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            
            # Add body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Add attachment if provided
            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment.add_header('Content-Disposition', 'attachment',
                                         filename=Path(attachment_path).name)
                    msg.attach(attachment)
            
            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend([e.strip() for e in cc.split(',')])
            if bcc:
                recipients.extend([e.strip() for e in bcc.split(',')])
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.sender_email, pwd)
                server.sendmail(self.sender_email, recipients, msg.as_string())
            
            return {'success': True, 'message': f'Email wysłany do {to_email}'}
            
        except smtplib.SMTPAuthenticationError:
            return {'success': False, 'message': 'Błąd autoryzacji. Sprawdź email i hasło.\nDla Gmail użyj App Password.'}
        except smtplib.SMTPException as e:
            return {'success': False, 'message': f'Błąd SMTP: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Błąd wysyłania: {str(e)}'}
    
    def test_connection(self, password: Optional[str] = None) -> Dict[str, Any]:
        """Test SMTP connection."""
        pwd = password or self.get_password()
        if not pwd:
            return {'success': False, 'message': 'Brak hasła'}
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.sender_email, pwd)
            return {'success': True, 'message': 'Połączenie OK!'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
