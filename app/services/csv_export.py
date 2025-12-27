"""
CSV export service for cost estimates.
"""

import csv
from typing import List, Dict, Any
from io import StringIO


class CSVExporter:
    """
    Handles exporting cost estimate data to CSV format.
    """
    
    @staticmethod
    def export_items_to_csv(items: List[Dict[str, Any]], filepath: str) -> bool:
        """
        Export cost items to a CSV file.
        
        Args:
            items: List of cost item dictionaries
            filepath: Path to save the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                
                # Header row
                writer.writerow([
                    "Nazwa", "Ilość", "JM", "Cena netto", "VAT %", 
                    "Netto", "VAT", "Brutto", "Kategoria", "Notatka"
                ])
                
                # Data rows
                for item in items:
                    writer.writerow([
                        item.get('name', ''),
                        f"{item.get('quantity', 0):.3f}".replace('.', ','),
                        item.get('unit', ''),
                        f"{item.get('price_unit_net', 0.0):.2f}".replace('.', ','),
                        item.get('vat_rate', 0),
                        f"{item.get('total_net', 0.0):.2f}".replace('.', ','),
                        f"{item.get('vat_value', 0.0):.2f}".replace('.', ','),
                        f"{item.get('total_gross', 0.0):.2f}".replace('.', ','),
                        item.get('category', ''),
                        item.get('note', '')
                    ])
            
            return True
        except (IOError, OSError) as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_string(items: List[Dict[str, Any]]) -> str:
        """
        Export cost items to CSV format string.
        
        Args:
            items: List of cost item dictionaries
            
        Returns:
            CSV formatted string
        """
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Header
        writer.writerow([
            "Nazwa", "Ilość", "JM", "Cena netto", "VAT %", 
            "Netto", "VAT", "Brutto", "Kategoria", "Notatka"
        ])
        
        # Data
        for item in items:
            writer.writerow([
                item.get('name', ''),
                f"{item.get('quantity', 0):.3f}".replace('.', ','),
                item.get('unit', ''),
                f"{item.get('price_unit_net', 0.0):.2f}".replace('.', ','),
                item.get('vat_rate', 0),
                f"{item.get('total_net', 0.0):.2f}".replace('.', ','),
                f"{item.get('vat_value', 0.0):.2f}".replace('.', ','),
                f"{item.get('total_gross', 0.0):.2f}".replace('.', ','),
                item.get('category', ''),
                item.get('note', '')
            ])
        
        return output.getvalue()
