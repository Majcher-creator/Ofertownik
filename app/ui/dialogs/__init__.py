"""
Dialog modules for the Ofertownik application.
"""

from .email_config_dialog import EmailConfigDialog
from .send_email_dialog import SendEmailDialog
from .history_dialog import HistoryDialog, CompareVersionsDialog, PreviewItemsDialog
from .create_from_existing_dialog import CreateFromExistingDialog
from .margin_dialog import MarginSettingsDialog

__all__ = [
    'EmailConfigDialog',
    'SendEmailDialog',
    'HistoryDialog',
    'CompareVersionsDialog', 
    'PreviewItemsDialog',
    'CreateFromExistingDialog',
    'MarginSettingsDialog'
]
