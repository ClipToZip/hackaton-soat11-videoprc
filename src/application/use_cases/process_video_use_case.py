"""
Use Case: Process Video
Orchestrates the video processing workflow
"""
import os
import zipfile
import logging
import tempfile
from typing import Optional
from src.domain.entities.video_entity import VideoEntity
from src.application.ports.storage_port import StoragePort
from src.application.ports.message_producer_port import MessageProducerPort
from src.application.services.video_processing_service import VideoProcessingService

logger = logging.getLogger(__name__)


class ProcessVideoUseCase:
    """Use case for processing video files"""
    
    def __init__(
        self,
        storage: StoragePort,
        message_producer: MessageProducerPort,
        video_service: VideoProcessingService
    ):
        """
        Initialize use case with required dependencies
        
        Args:
            storage: Storage adapter (S3)
            message_producer: Message producer adapter (Kafka)
            video_service: Video processing service
        """
        self.storage = storage
        self.message_producer = message_producer
        self.video_service = video_service
        logger.info("ProcessVideoUseCase inicializado")
    
    def execute(self, video_entity: VideoEntity, file_content: bytes, output_topic: str) -> bool:
        """
        Execute video processing workflow
        
        Args:
            video_entity: Video entity with metadata
            file_content: Video file content in bytes
            output_topic: Kafka topic to send completion message
            
        Returns:
            True if processing was successful, False otherwise
        """
        temp_video_path = None
        frame_paths = []
        temp_zip_path = None
        
        try:
            logger.info(f"=== Iniciando processamento do vídeo ===")
            logger.info(f"Video ID: {video_entity.video_id}")
            logger.info(f"Path: {video_entity.path}")
            
            # 1. Save video to temporary file
            temp_video_path = self._save_temp_video(file_content, video_entity.path)
            if not temp_video_path:
                return False
            
            # 2. Extract frames from video
            logger.info("Extraindo frames do vídeo...")
            frame_paths = self.video_service.extract_frames(temp_video_path, num_frames=4)
            
            if not frame_paths or len(frame_paths) == 0:
                logger.error("Nenhum frame foi extraído do vídeo")
                return False
            
            logger.info(f"{len(frame_paths)} frames extraídos com sucesso")
            
            # 3. Create ZIP with frames
            logger.info("Criando arquivo ZIP com as imagens...")
            temp_zip_path = self._create_zip_with_frames(frame_paths)
            
            if not temp_zip_path:
                return False
            
            # 4. Upload ZIP to S3
            zip_s3_key = self._get_zip_s3_key(video_entity.path)
            logger.info(f"Fazendo upload do ZIP para S3: {zip_s3_key}")
            
            upload_success = self.storage.upload_file(temp_zip_path, zip_s3_key)
            
            if not upload_success:
                logger.error("Falha ao fazer upload do ZIP para S3")
                return False
            
            logger.info("ZIP enviado com sucesso para S3")
            
            # 5. Send completion message to Kafka
            completion_message = {
                "video_id": video_entity.video_id,
                "path": zip_s3_key,
                "message": "Pronto para download"
            }
            
            logger.info(f"Enviando mensagem de conclusão para tópico '{output_topic}'")
            message_sent = self.message_producer.send_message(output_topic, completion_message)
            
            if not message_sent:
                logger.error("Falha ao enviar mensagem de conclusão")
                return False
            
            logger.info("=== Processamento concluído com sucesso ===")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante processamento do vídeo: {e}", exc_info=True)
            return False
            
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files(temp_video_path, frame_paths, temp_zip_path)
    
    def _save_temp_video(self, file_content: bytes, original_path: str) -> Optional[str]:
        """
        Save video content to temporary file
        
        Args:
            file_content: Video file content
            original_path: Original video path (to extract extension)
            
        Returns:
            Path to temporary video file, or None if error
        """
        try:
            # Get file extension
            _, ext = os.path.splitext(original_path)
            
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
            
            # Write content to file
            with os.fdopen(temp_fd, 'wb') as temp_file:
                temp_file.write(file_content)
            
            logger.info(f"Vídeo salvo temporariamente em: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Erro ao salvar vídeo temporário: {e}", exc_info=True)
            return None
    
    def _create_zip_with_frames(self, frame_paths: list) -> Optional[str]:
        """
        Create a ZIP file with extracted frames
        
        Args:
            frame_paths: List of frame file paths
            
        Returns:
            Path to ZIP file, or None if error
        """
        try:
            # Create temporary ZIP file
            temp_fd, temp_zip_path = tempfile.mkstemp(suffix='.zip')
            os.close(temp_fd)
            
            # Create ZIP and add frames
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for frame_path in frame_paths:
                    # Add file to ZIP with just the filename (no path)
                    arcname = os.path.basename(frame_path)
                    zipf.write(frame_path, arcname=arcname)
                    logger.info(f"Adicionado ao ZIP: {arcname}")
            
            logger.info(f"ZIP criado com sucesso: {temp_zip_path}")
            return temp_zip_path
            
        except Exception as e:
            logger.error(f"Erro ao criar ZIP: {e}", exc_info=True)
            return None
    
    def _get_zip_s3_key(self, original_path: str) -> str:
        """
        Generate S3 key for ZIP file based on original video path
        
        Args:
            original_path: Original video S3 path (e.g., "video/nome-do-video.mp4")
            
        Returns:
            S3 key for ZIP file (e.g., "zip/nome-do-video.zip")
        """
        # Get just the filename without extension
        filename = os.path.basename(original_path)
        filename_without_ext = os.path.splitext(filename)[0]
        return f"zip/{filename_without_ext}.zip"
    
    def _cleanup_temp_files(self, video_path: Optional[str], frame_paths: list, zip_path: Optional[str]):
        """
        Clean up all temporary files
        
        Args:
            video_path: Path to temporary video file
            frame_paths: List of frame file paths
            zip_path: Path to temporary ZIP file
        """
        logger.info("Limpando arquivos temporários...")
        
        # Remove video file
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"Vídeo temporário removido: {video_path}")
            except Exception as e:
                logger.warning(f"Erro ao remover vídeo temporário: {e}")
        
        # Remove frame files
        self.video_service.cleanup_files(frame_paths)
        
        # Remove ZIP file
        if zip_path and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                logger.info(f"ZIP temporário removido: {zip_path}")
            except Exception as e:
                logger.warning(f"Erro ao remover ZIP temporário: {e}")
        
        logger.info("Limpeza concluída")
