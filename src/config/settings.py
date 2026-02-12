"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Classe de configuração da aplicação"""
    
    # AWS SQS
    CLIPTOZIP_EVENTS_URL = os.getenv('CLIPTOZIP_EVENTS_URL')
    CLIPTOZIP_NOTIFICATIONS_URL = os.getenv('CLIPTOZIP_NOTIFICATIONS_URL')
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    
    # Database PostgreSQL
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT'))
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # Application
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    APP_NAME = os.getenv('APP_NAME')
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '3'))  # Número máximo de vídeos processando simultaneamente
    
    @classmethod
    def validate(cls):
        """Valida se as configurações obrigatórias estão presentes"""
        required_configs = [
            ('AWS_ACCESS_KEY_ID', cls.AWS_ACCESS_KEY_ID),
            ('AWS_SECRET_ACCESS_KEY', cls.AWS_SECRET_ACCESS_KEY),
            ('S3_BUCKET_NAME', cls.S3_BUCKET_NAME),
            ('DB_PASSWORD', cls.DB_PASSWORD),
            ('CLIPTOZIP_EVENTS_URL', cls.CLIPTOZIP_EVENTS_URL),
            ('CLIPTOZIP_NOTIFICATIONS_URL', cls.CLIPTOZIP_NOTIFICATIONS_URL),
        ]
        
        missing = [name for name, value in required_configs if not value]
        
        if missing:
            raise ValueError(f"Configurações obrigatórias ausentes: {', '.join(missing)}")
