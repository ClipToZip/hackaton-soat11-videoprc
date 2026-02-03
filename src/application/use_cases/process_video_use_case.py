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
from src.domain.entities.user_entity import UserEntity
from src.application.ports.storage_port import StoragePort
from src.application.ports.message_producer_port import MessageProducerPort
from src.application.ports.repository_port import VideoRepositoryPort
from src.application.services.video_processing_service import VideoProcessingService

logger = logging.getLogger(__name__)


class ProcessVideoUseCase:
    """Use case for processing video files"""
    
    def __init__(
        self,
        storage: StoragePort,
        message_producer: MessageProducerPort,
        video_service: VideoProcessingService,
        repository: VideoRepositoryPort
    ):
        """
        Initialize use case with required dependencies
        
        Args:
            storage: Storage adapter (S3)
            message_producer: Message producer adapter (Kafka)
            video_service: Video processing service
            repository: Video repository
        """
        self.storage = storage
        self.message_producer = message_producer
        self.video_service = video_service
        self.repository = repository
        logger.info("ProcessVideoUseCase inicializado")
    
    def execute(self, video_id: str, file_content: bytes, output_topic: str) -> bool:
        """
        Execute video processing workflow
        
        Args:
            video_id: ID do vídeo a ser processado
            file_content: Video file content in bytes
            output_topic: Kafka topic to send completion message
            
        Returns:
            True if processing was successful, False otherwise
        """
    def execute(self, video_id: str, file_content: bytes, output_topic: str) -> bool:
        """
        Execute video processing workflow
        
        Args:
            video_id: ID do vídeo a ser processado
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
            logger.info(f"Video ID: {video_id}")
            
            # 1. Buscar vídeo e usuário no banco de dados
            result = self.repository.get_video_with_user(video_id)
            if not result:
                logger.error(f"Vídeo não encontrado no banco: {video_id}")
                return False
            
            video_entity, user_entity = result
            logger.info(f"Vídeo encontrado: {video_entity.titulo or video_entity.video_name}")
            logger.info(f"Usuário: {user_entity.name} ({user_entity.email})")
            
            # 2. Verificar status do vídeo
            if video_entity.status != 1:
                logger.warning(f"Vídeo com status inválido: {video_entity.status}. Esperado: 1")
                return False
            
            # 3. Atualizar status para "processando" (2)
            if not self.repository.update_video_status(video_id, 2):
                logger.error("Falha ao atualizar status para processando")
                return False
            
            logger.info("Status atualizado para: 2 (Processando)")
            
            # 4. Save video to temporary file
            temp_video_path = self._save_temp_video(file_content, video_entity.video_name or "video.mp4")
            if not temp_video_path:
                self._handle_processing_error(video_id, video_entity, user_entity, output_topic)
                return False
            
            # 5. Extract frames from video
            logger.info("Extraindo frames do vídeo...")
            frame_paths = self.video_service.extract_frames(temp_video_path, num_frames=4)
            
            if not frame_paths or len(frame_paths) == 0:
                logger.error("Nenhum frame foi extraído do vídeo")
                self._handle_processing_error(video_id, video_entity, user_entity, output_topic)
                return False
            
            logger.info(f"{len(frame_paths)} frames extraídos com sucesso")
            
            # 6. Create ZIP with frames
            logger.info("Criando arquivo ZIP com as imagens...")
            temp_zip_path = self._create_zip_with_frames(frame_paths)
            
            if not temp_zip_path:
                self._handle_processing_error(video_id, video_entity, user_entity, output_topic)
                return False
            
            # 7. Upload ZIP to S3
            zip_s3_key = self._get_zip_s3_key(video_entity.video_name or f"{video_id}.mp4")
            logger.info(f"Fazendo upload do ZIP para S3: {zip_s3_key}")
            
            upload_success = self.storage.upload_file(temp_zip_path, zip_s3_key)
            
            if not upload_success:
                logger.error("Falha ao fazer upload do ZIP para S3")
                self._handle_processing_error(video_id, video_entity, user_entity, output_topic)
                return False
            
            logger.info("ZIP enviado com sucesso para S3")
            
            # 8. Atualizar status para "finalizado" (3) e salvar caminho do ZIP
            if not self.repository.update_video_status(video_id, 3, zip_s3_key):
                logger.error("Falha ao atualizar status para finalizado")
                return False
            
            logger.info("Status atualizado para: 3 (Finalizado)")
            
            # 9. Send success message to Kafka
            success_message = {
                "titulo": video_entity.titulo or video_entity.video_name or "Vídeo sem título",
                "status": "Finalizado",
                "mensagem": "Seu zip está pronto para download",
                "emailUsuario": user_entity.email,
                "nomeUsuario": user_entity.name or "Usuário"
            }
            
            logger.info(f"Enviando mensagem de conclusão para tópico '{output_topic}'")
            message_sent = self.message_producer.send_message(output_topic, success_message)
            
            if not message_sent:
                logger.error("Falha ao enviar mensagem de conclusão")
                return False
            
            logger.info("=== Processamento concluído com sucesso ===")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante processamento do vídeo: {e}", exc_info=True)
            # Tentar buscar dados do vídeo para enviar mensagem de erro
            try:
                result = self.repository.get_video_with_user(video_id)
                if result:
                    video_entity, user_entity = result
                    self._handle_processing_error(video_id, video_entity, user_entity, output_topic)
            except:
                pass
            return False
            
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files(temp_video_path, frame_paths, temp_zip_path)
    
    def _handle_processing_error(
        self, 
        video_id: str, 
        video_entity: VideoEntity, 
        user_entity: UserEntity, 
        output_topic: str
    ):
        """
        Trata erro no processamento do vídeo
        
        Args:
            video_id: ID do vídeo
            video_entity: Entidade do vídeo
            user_entity: Entidade do usuário
            output_topic: Tópico Kafka para enviar mensagem
        """
        try:
            # Atualizar status para "erro" (4)
            self.repository.update_video_status(video_id, 4)
            logger.info("Status atualizado para: 4 (Erro)")
            
            # Enviar mensagem de erro
            error_message = {
                "titulo": video_entity.titulo or video_entity.video_name or "Vídeo sem título",
                "status": "Erro",
                "mensagem": "Houve um erro no processamento do seu vídeo",
                "emailUsuario": user_entity.email,
                "nomeUsuario": user_entity.name or "Usuário"
            }
            
            self.message_producer.send_message(output_topic, error_message)
            logger.info("Mensagem de erro enviada ao tópico")
            
        except Exception as e:
            logger.error(f"Erro ao tratar falha no processamento: {e}", exc_info=True)
    
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
