"""
Unit tests for PDF preview service.
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_preview import PDFPreview


class TestPDFPreview:
    """Test suite for PDF preview functionality."""
    
    def test_preview_pdf_creates_temp_file(self):
        """Test that preview_pdf creates a temporary file with .pdf extension."""
        def mock_generator(path):
            # Symulacja generowania PDF
            with open(path, 'wb') as f:
                f.write(b'%PDF-1.4 fake pdf content')
        
        with patch.object(PDFPreview, 'open_file', return_value=True):
            temp_path = PDFPreview.preview_pdf(mock_generator)
            
            assert temp_path is not None
            assert temp_path.endswith('.pdf')
            assert 'ofertownik_preview_' in temp_path
            assert os.path.exists(temp_path)
            
            # Cleanup
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_preview_pdf_calls_generator(self):
        """Test that preview_pdf calls the PDF generator with correct arguments."""
        mock_generator = MagicMock()
        
        with patch.object(PDFPreview, 'open_file', return_value=True):
            temp_path = PDFPreview.preview_pdf(mock_generator, "arg1", "arg2", kwarg1="value1")
            
            # Sprawdź czy generator został wywołany
            assert mock_generator.called
            call_args = mock_generator.call_args
            
            # Pierwszy argument to ścieżka do pliku tymczasowego
            assert call_args[0][0].endswith('.pdf')
            # Pozostałe argumenty
            assert call_args[0][1:] == ("arg1", "arg2")
            assert call_args[1] == {"kwarg1": "value1"}
            
            # Cleanup
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_preview_pdf_calls_open_file(self):
        """Test that preview_pdf calls open_file with the temp file path."""
        def mock_generator(path):
            with open(path, 'wb') as f:
                f.write(b'test')
        
        with patch.object(PDFPreview, 'open_file', return_value=True) as mock_open:
            temp_path = PDFPreview.preview_pdf(mock_generator)
            
            # Sprawdź czy open_file został wywołany
            assert mock_open.called
            assert mock_open.call_args[0][0] == temp_path
            
            # Cleanup
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_preview_pdf_cleanup_on_open_failure(self):
        """Test that preview_pdf cleans up temp file if open_file fails."""
        def mock_generator(path):
            with open(path, 'wb') as f:
                f.write(b'test')
        
        with patch.object(PDFPreview, 'open_file', return_value=False):
            temp_path = PDFPreview.preview_pdf(mock_generator)
            
            # Jeśli otwarcie się nie powiodło, nie powinno być ścieżki
            assert temp_path is None
    
    def test_preview_pdf_returns_none_on_generator_error(self):
        """Test that preview_pdf returns None if generator raises an exception."""
        def failing_generator(path):
            raise Exception("Generator failed")
        
        with patch.object(PDFPreview, 'open_file', return_value=True):
            temp_path = PDFPreview.preview_pdf(failing_generator)
            
            assert temp_path is None

    def test_preview_pdf_returns_none_on_generator_false(self):
        """Test that preview_pdf returns None if generator signals failure."""
        def failing_generator(path):
            return False

        with patch.object(PDFPreview, 'open_file', return_value=True):
            temp_path = PDFPreview.preview_pdf(failing_generator)

            assert temp_path is None
    
    @patch('platform.system', return_value='Windows')
    def test_open_file_windows(self, mock_platform):
        """Test opening file on Windows."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            temp_path = f.name
        
        try:
            # Mock os.startfile tylko jeśli istnieje
            with patch('os.startfile', create=True) as mock_startfile:
                result = PDFPreview.open_file(temp_path)
                
                assert result is True
                assert mock_startfile.called
                assert mock_startfile.call_args[0][0] == temp_path
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('platform.system', return_value='Darwin')
    @patch('subprocess.Popen')
    def test_open_file_macos(self, mock_popen, mock_platform):
        """Test opening file on macOS."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            temp_path = f.name
        
        try:
            result = PDFPreview.open_file(temp_path)
            
            assert result is True
            assert mock_popen.called
            call_args = mock_popen.call_args
            assert call_args[0][0] == ["open", temp_path]
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('platform.system', return_value='Linux')
    @patch('subprocess.Popen')
    def test_open_file_linux(self, mock_popen, mock_platform):
        """Test opening file on Linux."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            temp_path = f.name
        
        try:
            result = PDFPreview.open_file(temp_path)
            
            assert result is True
            assert mock_popen.called
            call_args = mock_popen.call_args
            assert call_args[0][0] == ["xdg-open", temp_path]
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_open_file_nonexistent(self):
        """Test that open_file returns False for non-existent file."""
        result = PDFPreview.open_file('/nonexistent/path/to/file.pdf')
        assert result is False
    
    def test_cleanup_temp_file(self):
        """Test cleanup of temporary file."""
        # Utwórz plik tymczasowy
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            temp_path = f.name
        
        # Sprawdź, że plik istnieje
        assert os.path.exists(temp_path)
        
        # Usuń plik
        result = PDFPreview.cleanup_temp_file(temp_path)
        
        assert result is True
        assert not os.path.exists(temp_path)
    
    def test_cleanup_temp_file_nonexistent(self):
        """Test cleanup returns False for non-existent file."""
        result = PDFPreview.cleanup_temp_file('/nonexistent/path/to/file.pdf')
        assert result is False
    
    def test_cleanup_temp_file_none(self):
        """Test cleanup returns False for None path."""
        result = PDFPreview.cleanup_temp_file(None)
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
