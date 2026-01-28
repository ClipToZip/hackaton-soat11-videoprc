"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Classe de configuração da aplicação"""
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'video-events')
    KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'video-processed')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'video-processor-group')
    KAFKA_AUTO_OFFSET_RESET = os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    
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
        ]
        
        missing = [name for name, value in required_configs if not value]
        
        if missing:
            raise ValueError(f"Configurações obrigatórias ausentes: {', '.join(missing)}")
