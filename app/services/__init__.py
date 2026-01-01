"""Service layer for the application"""

from .database import Database
from .file_manager import FileManager
from .csv_export import CSVExporter
from .pdf_preview import PDFPreview

# Calculation modules
from .roof_calculations import (
    calculate_single_slope_roof,
    calculate_gable_roof,
    calculate_hip_roof,
    calculate_slant_length,
    degrees_to_radians
)
from .gutter_calculations import calculate_guttering
from .chimney_calculations import calculate_chimney_flashings, calculate_chimney_insulation
from .flashing_calculations import calculate_flashings_total
from .timber_calculations import calculate_timber_volume
from .felt_calculations import calculate_felt_roof
from .cost_calculations import compute_item, compute_totals

__all__ = [
    'Database',
    'FileManager', 
    'CSVExporter',
    'PDFPreview',
    # Calculation functions
    'calculate_single_slope_roof',
    'calculate_gable_roof',
    'calculate_hip_roof',
    'calculate_slant_length',
    'degrees_to_radians',
    'calculate_guttering',
    'calculate_chimney_flashings',
    'calculate_chimney_insulation',
    'calculate_flashings_total',
    'calculate_timber_volume',
    'calculate_felt_roof',
    'compute_item',
    'compute_totals',
]
