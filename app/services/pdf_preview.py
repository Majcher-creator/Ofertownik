"""
PDF Preview Service

Provides functionality to preview generated PDFs in the default system application
before saving them to a permanent location.
"""

import tempfile
import os
import platform
import subprocess
from typing import Callable, Optional


class PDFPreview:
    """Service for previewing PDF files in the default system application."""
    
    @staticmethod
    def preview_pdf(pdf_content_generator: Callable, *args, **kwargs) -> Optional[str]:
        """
        Generuje PDF do pliku tymczasowego i otwiera go w domyślnej aplikacji.
        
        Args:
            pdf_content_generator: Funkcja generująca PDF (przyjmuje ścieżkę jako pierwszy argument)
            *args, **kwargs: Argumenty przekazywane do generatora
            
        Returns:
            Optional[str]: Ścieżka do pliku tymczasowego lub None w przypadku błędu
        """
        try:
            # Tworzenie pliku tymczasowego z rozszerzeniem .pdf
            # delete=False zapewnia, że plik nie zostanie usunięty automatycznie
            with tempfile.NamedTemporaryFile(
                mode='wb',
                suffix='.pdf',
                prefix='ofertownik_preview_',
                delete=False
            ) as temp_file:
                temp_path = temp_file.name
            
            # Wywołanie generatora PDF z ścieżką do pliku tymczasowego
            pdf_content_generator(temp_path, *args, **kwargs)
            
            # Otworzenie pliku w domyślnej aplikacji
            if PDFPreview.open_file(temp_path):
                return temp_path
            else:
                # Jeśli nie udało się otworzyć, usuń plik tymczasowy
                try:
                    os.unlink(temp_path)
                except Exception:
                    # Ignore cleanup errors
                    pass
                return None
                
        except Exception:
            # W przypadku błędu zwróć None
            return None
    
    @staticmethod
    def open_file(path: str) -> bool:
        """
        Otwiera plik w domyślnej aplikacji systemowej.
        
        Args:
            path: Ścieżka do pliku do otwarcia
            
        Returns:
            bool: True jeśli otwarcie się powiodło, False w przeciwnym razie
        """
        if not os.path.exists(path):
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows: użyj os.startfile
                os.startfile(path)
                return True
                
            elif system == "Darwin":
                # macOS: użyj 'open'
                env = os.environ.copy()
                env["NO_AT_BRIDGE"] = "1"
                subprocess.Popen(
                    ["open", path],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
                
            else:
                # Linux: użyj 'xdg-open'
                env = os.environ.copy()
                env["NO_AT_BRIDGE"] = "1"
                subprocess.Popen(
                    ["xdg-open", path],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
                
        except Exception:
            return False
    
    @staticmethod
    def cleanup_temp_file(path: Optional[str]) -> bool:
        """
        Usuwa plik tymczasowy.
        
        Args:
            path: Ścieżka do pliku tymczasowego
            
        Returns:
            bool: True jeśli usunięcie się powiodło, False w przeciwnym razie
        """
        if not path or not os.path.exists(path):
            return False
        
        try:
            os.unlink(path)
            return True
        except Exception:
            return False
