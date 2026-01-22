"""Dialog submodules for the UI."""
from app.ui.dialogs.email_config_dialog import EmailConfigDialog
from app.ui.dialogs.send_email_dialog import SendEmailDialog

__all__ = ['EmailConfigDialog', 'SendEmailDialog']
"""
Dialog modules for the Ofertownik application.
"""

from .history_dialog import HistoryDialog, CompareVersionsDialog, PreviewItemsDialog
from .create_from_existing_dialog import CreateFromExistingDialog

__all__ = [
    'HistoryDialog',
    'CompareVersionsDialog', 
    'PreviewItemsDialog',
    'CreateFromExistingDialog'
]
