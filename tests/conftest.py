# Configuration for test environment
import os
import tempfile
from config import Config

class TestConfig(Config):
    """Test configuration that inherits from main Config but overrides for testing"""
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing (enable for CSRF-specific tests)
    
    # Use in-memory SQLite database for faster tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable file uploads for testing
    UPLOAD_FOLDER = tempfile.mkdtemp()
    
    # Use test secret key
    SECRET_KEY = 'test-secret-key-for-testing-only'
    
    # Disable email sending in tests
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = 'test@example.com'