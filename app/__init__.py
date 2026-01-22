"""
Ofertownik - Roofing Cost Estimator Application
Main application package

This package provides modular components for:
- Data models (Client, CostItem, Material)
- Services (Database, FileManager, CSVExporter, Calculation modules)
- UI components (Dialogs, Tabs, Styles) - requires tkinter
- Utilities (Formatting, Validation)
"""

__version__ = "4.7.0"
__author__ = "VICTOR TOMASZ MAJCHERCZYK"

# Export core components (always available)
from .models import Client, CostItem, Material
from .services import Database, FileManager
from .utils.formatting import fmt_money, fmt_money_plain
from .utils.validation import validate_cost_item, validate_client, validate_nip

# Export calculation services
from .services import (
    calculate_single_slope_roof,
    calculate_gable_roof,
    calculate_hip_roof,
    calculate_guttering,
    calculate_chimney_flashings,
    calculate_chimney_insulation,
    calculate_flashings_total,
    calculate_timber_volume,
    calculate_felt_roof,
    compute_item,
    compute_totals,
)

__all__ = [
    'Client',
    'CostItem',
    'Material',
    'Database',
    'FileManager',
    'fmt_money',
    'fmt_money_plain',
    'validate_cost_item',
    'validate_client',
    'validate_nip',
    # Calculation functions
    'calculate_single_slope_roof',
    'calculate_gable_roof',
    'calculate_hip_roof',
    'calculate_guttering',
    'calculate_chimney_flashings',
    'calculate_chimney_insulation',
    'calculate_flashings_total',
    'calculate_timber_volume',
    'calculate_felt_roof',
    'compute_item',
    'compute_totals',
]

# Export UI components (requires tkinter, optional)
try:
    from .ui.dialogs import ClientDialog, CostItemEditDialog, MaterialEditDialog
    __all__.extend(['ClientDialog', 'CostItemEditDialog', 'MaterialEditDialog'])
except ImportError:
    # tkinter not available, UI components not exported
    pass
