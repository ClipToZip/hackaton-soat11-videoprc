"""
Cliente S3 para buscar arquivos
"""
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from src.config.settings import Settings
from src.application.ports.storage_port import StoragePort

logger = logging.getLogger(__name__)


class S3Client(StoragePort):
    """Cliente para interagir com AWS S3"""
    
    def __init__(self):
        """Inicializa o cliente S3"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Settings.AWS_SECRET_ACCESS_KEY,
            region_name=Settings.AWS_REGION
        )
        self.bucket_name = Settings.S3_BUCKET_NAME
        logger.info(f"Cliente S3 inicializado para o bucket: {self.bucket_name}")
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Baixa um arquivo do S3
        
        Args:
            s3_key: Chave do arquivo no S3
            local_path: Caminho local onde salvar o arquivo
            
        Returns:
            True se o download foi bem-sucedido, False caso contrário
        """
        try:
            logger.info(f"Baixando arquivo {s3_key} do S3...")
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Arquivo salvo em: {local_path}")
            return True
        except ClientError as e:
            logger.error(f"Erro ao baixar arquivo {s3_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao baixar arquivo {s3_key}: {e}")
            return False
    
    def get_file_content(self, s3_key: str) -> Optional[bytes]:
        """
        Obtém o conteúdo de um arquivo do S3
        
        Args:
            s3_key: Chave do arquivo no S3
            
        Returns:
            Conteúdo do arquivo em bytes ou None em caso de erro
        """
        try:
            logger.info(f"Obtendo conteúdo do arquivo {s3_key} do S3...")
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read()
            logger.info(f"Arquivo {s3_key} lido com sucesso ({len(content)} bytes)")
            return content
        except ClientError as e:
            logger.error(f"Erro ao obter conteúdo do arquivo {s3_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter conteúdo do arquivo {s3_key}: {e}")
            return None
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Verifica se um arquivo existe no S3
        
        Args:
            s3_key: Chave do arquivo no S3
            
        Returns:
            True se o arquivo existe, False caso contrário
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
    
    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Faz upload de um arquivo para o S3
        
        Args:
            local_path: Caminho local do arquivo
            s3_key: Chave do arquivo no S3
            
        Returns:
            True se o upload foi bem-sucedido, False caso contrário
        """
        try:
            logger.info(f"Fazendo upload do arquivo {local_path} para S3 com chave {s3_key}...")
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"Arquivo {s3_key} enviado com sucesso para o S3")
            return True
        except ClientError as e:
            logger.error(f"Erro ao fazer upload do arquivo {s3_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao fazer upload do arquivo {s3_key}: {e}")
            return False

