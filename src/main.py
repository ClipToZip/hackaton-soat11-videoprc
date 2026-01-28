"""
Ponto de entrada da aplicação - FastAPI Server
"""
import logging
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config.settings import Settings
from src.adapters.input.consumers.kafka_consumer import KafkaS3Consumer
from src.adapters.input.routers import health_controller
from src.adapters.output.persistence.s3.s3_client import S3Client
from src.adapters.output.producers.kafka_producer import KafkaProducer
from src.application.services.video_processing_service import VideoProcessingService
from src.application.use_cases.process_video_use_case import ProcessVideoUseCase

# Variáveis globais para gerenciar o consumer e s3_client
kafka_consumer = None
s3_client = None
kafka_producer = None
process_video_use_case = None
consumer_thread = None
executor = None  # ThreadPoolExecutor para processamento paralelo


def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, Settings.LOG_LEVEL),
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def process_video_task(message_data, file_content: bytes):
    """
    Tarefa de processamento de vídeo (executada em thread separada)
    
    Args:
        message_data: VideoEntity com dados da mensagem do Kafka
        file_content: Conteúdo do arquivo do S3 em bytes
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== [Thread-{threading.current_thread().name}] Processando vídeo ===")
        logger.info(f"Video ID: {message_data.video_id}")
        logger.info(f"Path: {message_data.path}")
        logger.info(f"Tamanho do arquivo: {len(file_content)} bytes")
        
        # Execute video processing use case
        output_topic = Settings.KAFKA_OUTPUT_TOPIC
        success = process_video_use_case.execute(message_data, file_content, output_topic)
        
        if success:
            logger.info(f"✅ [Video ID: {message_data.video_id}] Vídeo processado com sucesso!")
        else:
            logger.error(f"❌ [Video ID: {message_data.video_id}] Falha ao processar vídeo")
        
        return success
            
    except Exception as e:
        logger.error(f"❌ [Video ID: {message_data.video_id}] Erro no processamento: {e}", exc_info=True)
        return False


def custom_message_handler(message_data, file_content: bytes):
    """
    Handler que submete o processamento para o ThreadPoolExecutor
    
    Args:
        message_data: VideoEntity com dados da mensagem do Kafka
        file_content: Conteúdo do arquivo do S3 em bytes
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Submete a tarefa para o executor (processamento assíncrono)
        future = executor.submit(process_video_task, message_data, file_content)
        logger.info(f"🎬 [Video ID: {message_data.video_id}] Tarefa submetida para processamento")
        
        # Log do número de tarefas em andamento
        # Note: _work_queue.qsize() pode não ser 100% preciso mas dá uma ideia
        logger.info(f"📊 Tarefas em processamento: ~{executor._work_queue.qsize() + len([t for t in threading.enumerate() if 'ThreadPoolExecutor' in t.name])}")
            
    except Exception as e:
        logger.error(f"Erro ao submeter tarefa: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    Inicializa recursos no startup e limpa no shutdown
    """
    logger = logging.getLogger(__name__)
    global kafka_consumer, s3_client, kafka_producer, process_video_use_case, consumer_thread, executor
    
    # Startup
    logger.info("🚀 Iniciando aplicação...")
    
    try:
        # Valida configurações
        Settings.validate()
        logger.info("✅ Configurações validadas com sucesso")
        
        # Inicializa ThreadPoolExecutor para processamento paralelo
        executor = ThreadPoolExecutor(max_workers=Settings.MAX_WORKERS)
        logger.info(f"✅ ThreadPoolExecutor inicializado com {Settings.MAX_WORKERS} workers")
        
        # Inicializa S3 Client
        s3_client = S3Client()
        logger.info("✅ S3 Client inicializado")
        
        # Inicializa Kafka Producer
        kafka_producer = KafkaProducer()
        logger.info("✅ Kafka Producer inicializado")
        
        # Inicializa Video Processing Service
        video_service = VideoProcessingService()
        logger.info("✅ Video Processing Service inicializado")
        
        # Inicializa Use Case
        process_video_use_case = ProcessVideoUseCase(
            storage=s3_client,
            message_producer=kafka_producer,
            video_service=video_service
        )
        logger.info("✅ Process Video Use Case inicializado")
        
        # Inicializa Kafka Consumer
        kafka_consumer = KafkaS3Consumer(message_handler=custom_message_handler)
        logger.info("✅ Kafka Consumer inicializado")
        
        # Inicia o consumer em uma thread separada
        consumer_thread = threading.Thread(target=kafka_consumer.start, daemon=True)
        consumer_thread.start()
        logger.info("✅ Kafka Consumer iniciado em background")
        
        logger.info("🎉 Aplicação iniciada com sucesso!")
        
    except ValueError as e:
        logger.error(f"❌ Erro de configuração: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar aplicação: {e}", exc_info=True)
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    
    if kafka_consumer:
        kafka_consumer.stop()
        logger.info("✅ Kafka Consumer encerrado")
    
    if executor:
        logger.info("Aguardando finalização de tarefas em andamento...")
        executor.shutdown(wait=True, cancel_futures=False)
        logger.info("✅ ThreadPoolExecutor encerrado")
    
    if kafka_producer:
        kafka_producer.close()
        logger.info("✅ Kafka Producer encerrado")
    
    if consumer_thread and consumer_thread.is_alive():
        consumer_thread.join(timeout=5)
        logger.info("✅ Thread do consumer finalizada")
    
    logger.info("👋 Aplicação encerrada")


# Configura logging antes de criar a aplicação
setup_logging()
logger = logging.getLogger(__name__)

# Cria a aplicação FastAPI
app = FastAPI(
    title="Video Processor - Kafka S3",
    description="Aplicação para processar eventos do Kafka e buscar arquivos do S3",
    version="1.0.0",
    docs_url=f"/{Settings.APP_NAME}/apidocs",
    redoc_url=f"/{Settings.APP_NAME}/redocs",
    openapi_url=f"/{Settings.APP_NAME}/openapi.json",
    lifespan=lifespan
)

app.include_router(health_controller.router, prefix=f"/{Settings.APP_NAME}", tags=["Health"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
