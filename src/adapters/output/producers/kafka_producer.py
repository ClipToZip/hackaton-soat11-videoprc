"""
Kafka Producer - sends messages to Kafka topics
"""
import json
import logging
from typing import Dict, Any
from confluent_kafka import Producer, KafkaException
from src.config.settings import Settings
from src.application.ports.message_producer_port import MessageProducerPort

logger = logging.getLogger(__name__)


class KafkaProducer(MessageProducerPort):
    """Kafka producer implementation"""
    
    def __init__(self):
        """Initialize Kafka producer"""
        self.config = {
            'bootstrap.servers': Settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'video-processor-producer'
        }
        
        self.producer = Producer(self.config)
        logger.info("Kafka Producer inicializado")
    
    def _delivery_callback(self, err, msg):
        """
        Callback for message delivery confirmation
        
        Args:
            err: Error if message delivery failed
            msg: Message that was delivered
        """
        if err:
            logger.error(f"Falha ao enviar mensagem: {err}")
        else:
            logger.info(f"Mensagem enviada com sucesso para {msg.topic()} [{msg.partition()}]")
    
    def send_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to a Kafka topic
        
        Args:
            topic: Topic name
            message: Message data as dictionary
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Convert message to JSON
            message_json = json.dumps(message)
            
            # Send message
            self.producer.produce(
                topic=topic,
                value=message_json.encode('utf-8'),
                callback=self._delivery_callback
            )
            
            # Wait for message to be delivered
            self.producer.flush()
            
            logger.info(f"Mensagem enviada para tópico '{topic}': {message}")
            return True
            
        except KafkaException as e:
            logger.error(f"Erro ao enviar mensagem para Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar mensagem: {e}", exc_info=True)
            return False
    
    def close(self):
        """Close the producer and flush pending messages"""
        self.producer.flush()
        logger.info("Kafka Producer encerrado")
