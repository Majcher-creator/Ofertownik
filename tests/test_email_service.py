"""Tests for email service functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.email_service import EmailService


class TestEmailService:
    """Test EmailService class."""
    
    def test_email_service_initialization(self):
        """Test EmailService initializes with default values."""
        service = EmailService()
        assert service.smtp_server == ""
        assert service.smtp_port == 587
        assert service.use_tls is True
        assert service.sender_email == ""
        assert service.sender_name == ""
    
    def test_configure_email_service(self):
        """Test configuring email service settings."""
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com",
            sender_name="Test User",
            use_tls=True
        )
        
        assert service.smtp_server == "smtp.gmail.com"
        assert service.smtp_port == 587
        assert service.sender_email == "test@example.com"
        assert service.sender_name == "Test User"
        assert service.use_tls is True
    
    def test_configure_with_default_sender_name(self):
        """Test that sender_name defaults to sender_email if not provided."""
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com"
        )
        
        assert service.sender_name == "test@example.com"
    
    def test_providers_configuration(self):
        """Test that provider configurations are defined correctly."""
        assert 'Gmail' in EmailService.PROVIDERS
        assert 'Outlook/Hotmail' in EmailService.PROVIDERS
        assert 'Office 365' in EmailService.PROVIDERS
        assert 'Yahoo' in EmailService.PROVIDERS
        assert 'Własny serwer' in EmailService.PROVIDERS
        
        gmail_config = EmailService.PROVIDERS['Gmail']
        assert gmail_config['smtp_server'] == 'smtp.gmail.com'
        assert gmail_config['smtp_port'] == 587
        assert gmail_config['use_tls'] is True
    
    @patch('app.services.email_service.KEYRING_AVAILABLE', True)
    @patch('app.services.email_service.keyring', create=True)
    def test_save_password(self, mock_keyring):
        """Test saving password to keyring."""
        service = EmailService()
        service.sender_email = "test@example.com"
        
        result = service.save_password("test_password")
        
        assert result is True
        mock_keyring.set_password.assert_called_once_with(
            EmailService.KEYRING_SERVICE,
            "test@example.com",
            "test_password"
        )
    
    @patch('app.services.email_service.KEYRING_AVAILABLE', True)
    @patch('app.services.email_service.keyring', create=True)
    def test_get_password(self, mock_keyring):
        """Test retrieving password from keyring."""
        mock_keyring.get_password.return_value = "test_password"
        
        service = EmailService()
        service.sender_email = "test@example.com"
        
        password = service.get_password()
        
        assert password == "test_password"
        mock_keyring.get_password.assert_called_once_with(
            EmailService.KEYRING_SERVICE,
            "test@example.com"
        )
    
    @patch('app.services.email_service.KEYRING_AVAILABLE', False)
    def test_save_password_without_keyring(self):
        """Test that save_password returns False when keyring is not available."""
        service = EmailService()
        service.sender_email = "test@example.com"
        
        result = service.save_password("test_password")
        
        assert result is False
    
    @patch('app.services.email_service.KEYRING_AVAILABLE', False)
    def test_get_password_without_keyring(self):
        """Test that get_password returns None when keyring is not available."""
        service = EmailService()
        service.sender_email = "test@example.com"
        
        password = service.get_password()
        
        assert password is None
    
    def test_send_email_without_configuration(self):
        """Test that send_email fails when not configured."""
        service = EmailService()
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test",
            body="Test message"
        )
        
        assert result['success'] is False
        assert 'nie jest skonfigurowany' in result['message']
    
    def test_send_email_without_password(self):
        """Test that send_email fails when password is not available."""
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com"
        )
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test",
            body="Test message"
        )
        
        assert result['success'] is False
        assert 'Brak hasła' in result['message']
    
    @patch('app.services.email_service.smtplib.SMTP')
    @patch('app.services.email_service.ssl.create_default_context')
    @patch.object(EmailService, 'get_password', return_value='test_password')
    def test_send_email_success(self, mock_get_password, mock_ssl_context, mock_smtp):
        """Test successful email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com",
            sender_name="Test User"
        )
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test message body"
        )
        
        assert result['success'] is True
        assert 'wysłany' in result['message']
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.sendmail.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP')
    @patch('app.services.email_service.ssl.create_default_context')
    def test_send_email_with_password_parameter(self, mock_ssl_context, mock_smtp):
        """Test sending email with password provided as parameter."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com"
        )
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test",
            body="Test message",
            password="provided_password"
        )
        
        assert result['success'] is True
        mock_server.login.assert_called_with("test@example.com", "provided_password")
    
    @patch('app.services.email_service.smtplib.SMTP')
    @patch('app.services.email_service.ssl.create_default_context')
    @patch.object(EmailService, 'get_password', return_value='test_password')
    def test_test_connection_success(self, mock_get_password, mock_ssl_context, mock_smtp):
        """Test successful connection test."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com"
        )
        
        result = service.test_connection()
        
        assert result['success'] is True
        assert 'OK' in result['message']
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
    
    def test_test_connection_without_password(self):
        """Test that test_connection fails when password is not available."""
        service = EmailService()
        service.configure(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com"
        )
        
        result = service.test_connection()
        
        assert result['success'] is False
        assert 'Brak hasła' in result['message']
