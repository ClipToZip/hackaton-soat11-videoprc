"""
SQS Producer - sends messages to SQS queues
"""
import json
import logging
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from src.config.settings import Settings
from src.application.ports.message_producer_port import MessageProducerPort

logger = logging.getLogger(__name__)


class SQSProducer(MessageProducerPort):
    """SQS producer implementation"""
    
    def __init__(self):
        """Initialize SQS producer"""
        self.sqs_client = boto3.client(
            'sqs',
            region_name=Settings.AWS_REGION,
            aws_access_key_id=Settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Settings.AWS_SECRET_ACCESS_KEY
        )
        
        logger.info("SQS Producer inicializado")
    
    def send_message(self, queue_url: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to an SQS queue
        
        Args:
            queue_url: URL da fila SQS
            message: Message data as dictionary
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Convert message to JSON
            message_json = json.dumps(message)
            
            # Send message
            response = self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message_json
            )
            
            message_id = response.get('MessageId')
            logger.info(f"Mensagem enviada para fila '{queue_url}' - MessageId: {message_id}")
            logger.debug(f"Conteúdo da mensagem: {message}")
            
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao enviar mensagem para SQS: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar mensagem: {e}", exc_info=True)
            return False
    
    def close(self):
        """Close the producer (no-op for SQS, but kept for interface compatibility)"""
        logger.info("SQS Producer encerrado")
