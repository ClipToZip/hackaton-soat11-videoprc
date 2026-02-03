"""
PostgreSQL Database Connection
Gerencia a conexão com o banco de dados PostgreSQL
"""
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
from src.config.settings import Settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Gerenciador de conexão com PostgreSQL"""
    
    def __init__(self):
        """Inicializa o gerenciador de conexão"""
        self.connection = None
        
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = psycopg2.connect(
                host=Settings.DB_HOST,
                port=Settings.DB_PORT,
                database=Settings.DB_NAME,
                user=Settings.DB_USER,
                password=Settings.DB_PASSWORD
            )
            logger.info("Conexão com PostgreSQL estabelecida com sucesso")
            return self.connection
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
            raise
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão com PostgreSQL fechada")
    
    def get_connection(self):
        """
        Retorna a conexão ativa ou cria uma nova
        
        Returns:
            Conexão do psycopg2
        """
        if not self.connection or self.connection.closed:
            return self.connect()
        return self.connection
