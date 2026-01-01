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
