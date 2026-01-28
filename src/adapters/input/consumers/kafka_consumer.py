"""
Consumer Kafka que processa eventos e busca arquivos do S3
"""
import json
import logging
import time
from typing import Callable, Optional
from confluent_kafka import Consumer, KafkaError, KafkaException
from src.config.settings import Settings
from src.adapters.output.persistence.s3.s3_client import S3Client
from src.domain.entities.video_entity import VideoEntity

logger = logging.getLogger(__name__)


class KafkaS3Consumer:
    """Consumer Kafka que busca arquivos do S3 baseado em eventos"""
    
    def __init__(self, message_handler: Optional[Callable] = None):
        """
        Inicializa o consumer Kafka
        
        Args:
            message_handler: Função customizada para processar a mensagem e arquivo do S3.
                           Recebe (message_data: dict, file_content: bytes) como parâmetros.
        """
        self.config = {
            'bootstrap.servers': Settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': Settings.KAFKA_GROUP_ID,
            'auto.offset.reset': Settings.KAFKA_AUTO_OFFSET_RESET,
            'enable.auto.commit': True,
        }
        
        self.consumer = Consumer(self.config)
        self.s3_client = S3Client()
        self.message_handler = message_handler
        self.running = False
        
        logger.info(f"Consumer Kafka inicializado para o tópico: {Settings.KAFKA_TOPIC}")
    
    def _default_message_handler(self, message_data: dict, file_content: bytes):
        """
        Handler padrão para processar mensagem e arquivo
        
        Args:
            message_data: Dados da mensagem do Kafka
            file_content: Conteúdo do arquivo do S3
        """
        logger.info(f"Processando mensagem: {message_data}")
        logger.info(f"Tamanho do arquivo: {len(file_content)} bytes")
        # Adicione aqui o processamento do arquivo conforme necessário
    
    def process_message(self, message):
        """
        Processa uma mensagem do Kafka
        
        Args:
            message: Mensagem do Kafka
        """
        try:
            # Parse da mensagem
            message_value = message.value().decode('utf-8')
            message_data = json.loads(message_value)
            video_entity = VideoEntity(**message_data)
            
            logger.info(f"Mensagem recebida: {video_entity}")
            
            # Busca o arquivo do S3
            file_content = self.s3_client.get_file_content(video_entity.path)
            
            if file_content is None:
                logger.error(f"Falha ao obter conteúdo do arquivo {video_entity.path}")
                return
            
            # Processa o arquivo usando o handler
            handler = self.message_handler or self._default_message_handler
            handler(video_entity, file_content)
            
            logger.info(f"Mensagem processada com sucesso para o arquivo: {video_entity.path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da mensagem: {e}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
    
    def start(self):
        """Inicia o consumer e começa a processar mensagens"""
        try:
            self.consumer.subscribe([Settings.KAFKA_TOPIC])
            self.running = True
            
            logger.info(f"Consumer iniciado. Aguardando mensagens no tópico '{Settings.KAFKA_TOPIC}'...")
            
            topic_not_found_count = 0
            max_topic_warnings = 5
            
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(f"Fim da partição alcançado: {msg.topic()} [{msg.partition()}]")
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        # Tópico não existe - não crashar a aplicação
                        topic_not_found_count += 1
                        if topic_not_found_count <= max_topic_warnings:
                            logger.warning(f"⚠️  Tópico '{Settings.KAFKA_TOPIC}' não encontrado. Aguardando criação do tópico... (tentativa {topic_not_found_count})")
                            logger.info(f"💡 Crie o tópico com: kafka-topics --create --topic {Settings.KAFKA_TOPIC} --bootstrap-server {Settings.KAFKA_BOOTSTRAP_SERVERS} --partitions 1 --replication-factor 1")
                        elif topic_not_found_count == max_topic_warnings + 1:
                            logger.warning(f"⚠️  Tópico ainda não encontrado. Reduzindo frequência de avisos...")
                        
                        # Aguarda antes de tentar novamente
                        time.sleep(5)
                        continue
                    elif msg.error().code() in [KafkaError._ALL_BROKERS_DOWN, KafkaError._TRANSPORT]:
                        logger.error(f"❌ Erro de conexão com Kafka: {msg.error()}. Tentando reconectar em 10s...")
                        time.sleep(10)
                        continue
                    else:
                        logger.error(f"Erro do Kafka: {msg.error()}")
                        time.sleep(5)
                        continue
                else:
                    # Reset do contador quando mensagens começam a chegar
                    if topic_not_found_count > 0:
                        logger.info(f"✅ Tópico '{Settings.KAFKA_TOPIC}' agora disponível! Processando mensagens...")
                        topic_not_found_count = 0
                    
                    self.process_message(msg)
                    
        except KeyboardInterrupt:
            logger.info("Interrupção pelo usuário (Ctrl+C)")
        except Exception as e:
            logger.error(f"Erro no consumer: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Para o consumer e fecha a conexão"""
        logger.info("Encerrando consumer...")
        self.running = False
        self.consumer.close()
        logger.info("Consumer encerrado")
