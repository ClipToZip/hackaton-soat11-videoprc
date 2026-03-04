"""
Consumer SQS que processa mensagens e busca arquivos do S3
"""
import json
import logging
import time
from typing import Callable, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from src.config.settings import Settings
from src.adapters.output.persistence.s3.s3_client import S3Client

logger = logging.getLogger(__name__)


class SQSConsumer:
    """Consumer SQS que busca arquivos do S3 baseado em mensagens"""
    
    def __init__(self, message_handler: Optional[Callable] = None):
        """
        Inicializa o consumer SQS
        
        Args:
            message_handler: Função customizada para processar a mensagem e arquivo do S3.
                           Recebe (video_id: str, file_content: bytes) como parâmetros.
        """
        self.sqs_client = boto3.client(
            'sqs',
            region_name=Settings.AWS_REGION,
            aws_access_key_id=Settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Settings.AWS_SECRET_ACCESS_KEY
        )
        
        self.queue_url = Settings.CLIPTOZIP_EVENTS_URL
        self.s3_client = S3Client()
        self.message_handler = message_handler
        self.running = False
        
        logger.info(f"Consumer SQS inicializado para a fila: {self.queue_url}")
    
    def _default_message_handler(self, video_id: str, file_content: bytes):
        """
        Handler padrão para processar mensagem e arquivo
        
        Args:
            video_id: ID do vídeo
            file_content: Conteúdo do arquivo do S3
        """
        logger.info(f"Processando vídeo ID: {video_id}")
        logger.info(f"Tamanho do arquivo: {len(file_content)} bytes")
    
    def process_message(self, message: dict):
        """
        Processa uma mensagem do SQS
        
        Args:
            message: Mensagem do SQS
        """
        try:
            # Parse da mensagem
            message_body = message['Body']
            message_data = json.loads(message_body)
            
            # Extrair video_id e path da mensagem
            video_id = message_data.get('video_id')
            video_path = message_data.get('path')
            
            if not video_id:
                logger.error("Mensagem sem video_id")
                return False
            
            if not video_path:
                logger.error(f"Mensagem sem path para o vídeo {video_id}")
                return False
            
            logger.info(f"Mensagem recebida - Video ID: {video_id}, Path: {video_path}")
            
            # Busca o arquivo do S3
            file_content = self.s3_client.get_file_content(video_path)
            
            if file_content is None:
                logger.error(f"Falha ao obter conteúdo do arquivo {video_path}")
                return False
            
            # Processa o arquivo usando o handler
            handler = self.message_handler or self._default_message_handler
            handler(video_id, file_content)
            
            logger.info(f"Mensagem processada com sucesso para o vídeo: {video_id}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da mensagem: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            return False
    
    def delete_message(self, receipt_handle: str):
        """
        Remove mensagem da fila após processamento bem-sucedido
        
        Args:
            receipt_handle: Receipt handle da mensagem
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.debug("Mensagem deletada da fila")
        except ClientError as e:
            logger.error(f"Erro ao deletar mensagem: {e}")
    
    def start(self):
        """Inicia o consumer e começa a processar mensagens"""
        try:
            self.running = True
            
            logger.info(f"Consumer iniciado. Aguardando mensagens na fila '{self.queue_url}'...")
            
            while self.running:
                try:
                    # Recebe mensagens do SQS (long polling)
                    response = self.sqs_client.receive_message(
                        QueueUrl=self.queue_url,
                        MaxNumberOfMessages=1,
                        WaitTimeSeconds=20,  # Long polling
                        VisibilityTimeout=60  # Tempo que a mensagem fica invisível
                    )
                    
                    messages = response.get('Messages', [])
                    
                    if not messages:
                        continue
                    
                    for message in messages:
                        receipt_handle = message['ReceiptHandle']
                        
                        # Processa a mensagem
                        success = self.process_message(message)
                        
                        # Se processado com sucesso, remove da fila
                        if success:
                            self.delete_message(receipt_handle)
                        else:
                            logger.warning(f"Mensagem não foi processada com sucesso. Ela ficará visível novamente após o timeout.")
                
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                        logger.error(f"❌ Fila SQS não encontrada: {self.queue_url}")
                        logger.info("💡 Verifique se a fila foi criada na AWS e se a URL está correta")
                        time.sleep(10)
                    else:
                        logger.error(f"Erro do SQS: {e}")
                        time.sleep(5)
                except BotoCoreError as e:
                    logger.error(f"Erro de conexão com AWS: {e}. Tentando reconectar em 10s...")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            logger.info("Interrupção pelo usuário (Ctrl+C)")
        except Exception as e:
            logger.error(f"Erro no consumer: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Para o consumer"""
        logger.info("Encerrando consumer SQS...")
        self.running = False
        logger.info("Consumer SQS encerrado")
