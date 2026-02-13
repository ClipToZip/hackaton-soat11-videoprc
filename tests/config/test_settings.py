"""
Unit tests for Settings
"""
import pytest
import os
from unittest.mock import patch
from src.config.settings import Settings


class TestSettings:
    """Test cases for Settings"""
    
    def test_settings_aws_sqs_urls(self):
        """Test AWS SQS URL settings"""
        # These are read from environment variables, so just check they exist
        assert Settings.CLIPTOZIP_EVENTS_URL is not None
        assert Settings.CLIPTOZIP_NOTIFICATIONS_URL is not None
        assert 'sqs' in Settings.CLIPTOZIP_EVENTS_URL.lower()
        assert 'sqs' in Settings.CLIPTOZIP_NOTIFICATIONS_URL.lower()
    
    def test_settings_aws_credentials(self):
        """Test AWS credentials settings"""
        # These are read from environment, just verify they're set
        assert Settings.AWS_ACCESS_KEY_ID is not None
        assert Settings.AWS_SECRET_ACCESS_KEY is not None
        assert Settings.AWS_REGION is not None
        assert Settings.S3_BUCKET_NAME is not None
    
    def test_settings_database_config(self):
        """Test database configuration settings"""
        # These are read from environment, just verify they're set
        assert Settings.DB_HOST is not None
        assert Settings.DB_PORT is not None
        assert Settings.DB_NAME is not None
        assert Settings.DB_USER is not None
        assert Settings.DB_PASSWORD is not None
        assert isinstance(Settings.DB_PORT, int)
    
    def test_settings_application_config(self):
        """Test application configuration settings"""
        # These are read from environment, just verify they're set
        assert Settings.LOG_LEVEL is not None
        assert Settings.APP_NAME is not None
        assert Settings.MAX_WORKERS is not None
        assert isinstance(Settings.MAX_WORKERS, int)
    
    def test_settings_default_values(self, monkeypatch):
        """Test default values when env vars not set"""
        # Remove specific env vars
        monkeypatch.delenv('AWS_REGION', raising=False)
        monkeypatch.delenv('LOG_LEVEL', raising=False)
        monkeypatch.delenv('MAX_WORKERS', raising=False)
        
        # Reload settings
        from importlib import reload
        from src.config import settings
        reload(settings)
        
        # Check defaults exist
        assert settings.Settings.AWS_REGION is not None
        assert settings.Settings.LOG_LEVEL is not None
    
    def test_validate_all_configs_present(self):
        """Test validation with all required configs present"""
        # Should not raise any exception
        Settings.validate()
    
    @patch('src.config.settings.load_dotenv')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'S3_BUCKET_NAME': 'test-bucket',
        'DB_PASSWORD': 'test',
        'CLIPTOZIP_EVENTS_URL': 'test',
        'CLIPTOZIP_NOTIFICATIONS_URL': 'test',
        'DB_PORT': '5432',
        'MAX_WORKERS': '3'
    })
    def test_validate_missing_aws_access_key(self, mock_load_dotenv):
        """Test validation fails when AWS_ACCESS_KEY_ID is missing"""
        import sys
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        if 'src.config' in sys.modules:
            del sys.modules['src.config']
        
        from src.config import settings
        
        with pytest.raises(ValueError) as exc_info:
            settings.Settings.validate()
        
        assert 'AWS_ACCESS_KEY_ID' in str(exc_info.value)
    
    @patch('src.config.settings.load_dotenv')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': '',
        'S3_BUCKET_NAME': 'test-bucket',
        'DB_PASSWORD': 'test',
        'CLIPTOZIP_EVENTS_URL': 'test',
        'CLIPTOZIP_NOTIFICATIONS_URL': 'test',
        'DB_PORT': '5432',
        'MAX_WORKERS': '3'
    })
    def test_validate_missing_aws_secret_key(self, mock_load_dotenv):
        """Test validation fails when AWS_SECRET_ACCESS_KEY is missing"""
        import sys
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        if 'src.config' in sys.modules:
            del sys.modules['src.config']
        
        from src.config import settings
        
        with pytest.raises(ValueError) as exc_info:
            settings.Settings.validate()
        
        assert 'AWS_SECRET_ACCESS_KEY' in str(exc_info.value)
    
    @patch('src.config.settings.load_dotenv')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'S3_BUCKET_NAME': '',
        'DB_PASSWORD': 'test',
        'CLIPTOZIP_EVENTS_URL': 'test',
        'CLIPTOZIP_NOTIFICATIONS_URL': 'test',
        'DB_PORT': '5432',
        'MAX_WORKERS': '3'
    })
    def test_validate_missing_s3_bucket(self, mock_load_dotenv):
        """Test validation fails when S3_BUCKET_NAME is missing"""
        import sys
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        if 'src.config' in sys.modules:
            del sys.modules['src.config']
        
        from src.config import settings
        
        with pytest.raises(ValueError) as exc_info:
            settings.Settings.validate()
        
        assert 'S3_BUCKET_NAME' in str(exc_info.value)
    
    @patch('src.config.settings.load_dotenv')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'S3_BUCKET_NAME': 'test',
        'DB_PASSWORD': '',
        'CLIPTOZIP_EVENTS_URL': 'test',
        'CLIPTOZIP_NOTIFICATIONS_URL': 'test',
        'DB_PORT': '5432',
        'MAX_WORKERS': '3'
    })
    def test_validate_missing_db_password(self, mock_load_dotenv):
        """Test validation fails when DB_PASSWORD is missing"""
        import sys
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        if 'src.config' in sys.modules:
            del sys.modules['src.config']
        
        from src.config import settings
        
        with pytest.raises(ValueError) as exc_info:
            settings.Settings.validate()
        
        assert 'DB_PASSWORD' in str(exc_info.value)
    
    @patch('src.config.settings.load_dotenv')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'S3_BUCKET_NAME': 'test',
        'DB_PASSWORD': 'test',
        'CLIPTOZIP_EVENTS_URL': '',
        'CLIPTOZIP_NOTIFICATIONS_URL': '',
        'DB_PORT': '5432',
        'MAX_WORKERS': '3'
    })
    def test_validate_missing_sqs_urls(self, mock_load_dotenv):
        """Test validation fails when SQS URLs are missing"""
        import sys
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        if 'src.config' in sys.modules:
            del sys.modules['src.config']
        
        from src.config import settings
        
        with pytest.raises(ValueError) as exc_info:
            settings.Settings.validate()
        
        assert 'CLIPTOZIP_EVENTS_URL' in str(exc_info.value) or 'CLIPTOZIP_NOTIFICATIONS_URL' in str(exc_info.value)
    
    @patch('src.config.settings.load_dotenv')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'S3_BUCKET_NAME': '',
        'DB_PASSWORD': '',
        'CLIPTOZIP_EVENTS_URL': 'test',
        'CLIPTOZIP_NOTIFICATIONS_URL': 'test',
        'DB_PORT': '5432',
        'MAX_WORKERS': '3'
    })
    def test_validate_multiple_missing_configs(self, mock_load_dotenv):
        """Test validation fails with multiple missing configs"""
        import sys
        if 'src.config.settings' in sys.modules:
            del sys.modules['src.config.settings']
        if 'src.config' in sys.modules:
            del sys.modules['src.config']
        
        from src.config import settings
        
        with pytest.raises(ValueError) as exc_info:
            settings.Settings.validate()
        
        error_msg = str(exc_info.value)
        # Should mention multiple missing configs
        assert 'ausentes' in error_msg or 'missing' in error_msg.lower()
    
    def test_db_port_as_integer(self):
        """Test DB_PORT is converted to integer"""
        assert isinstance(Settings.DB_PORT, int)
    
    def test_max_workers_as_integer(self):
        """Test MAX_WORKERS is converted to integer"""
        assert isinstance(Settings.MAX_WORKERS, int)
