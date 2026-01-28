"""
Video Processing Service - Extracts frames from video files
"""
import os
import cv2
import logging
import tempfile
from typing import List, Optional

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """Service for processing video files"""
    
    def __init__(self):
        """Initialize video processing service"""
        logger.info("Video Processing Service inicializado")
    
    def extract_frames(self, video_path: str, num_frames: int = 4) -> Optional[List[str]]:
        """
        Extract frames from a video file
        
        Args:
            video_path: Path to the video file
            num_frames: Number of frames to extract
            
        Returns:
            List of paths to extracted frame images, or None if error
        """
        frame_paths = []
        
        try:
            # Open video file
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                logger.error(f"Erro ao abrir o vídeo: {video_path}")
                return None
            
            # Get video properties
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Vídeo carregado: {total_frames} frames, {fps} FPS")
            
            # Calculate frame intervals
            if total_frames < num_frames:
                logger.warning(f"Vídeo tem menos frames ({total_frames}) que o solicitado ({num_frames})")
                num_frames = total_frames
            
            # Distribute frames evenly throughout the video
            # Calculate positions to extract frames from start, middle, and end
            frame_positions = []
            if num_frames == 1:
                frame_positions = [total_frames // 2]
            else:
                # Distribute frames evenly across the video duration
                step = (total_frames - 1) / (num_frames - 1)
                frame_positions = [int(i * step) for i in range(num_frames)]
            
            logger.info(f"Extraindo frames nas posições: {frame_positions}")
            
            # Extract frames
            for i, frame_number in enumerate(frame_positions):
                
                # Set video position
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                # Read frame
                ret, frame = video.read()
                
                if not ret:
                    logger.warning(f"Não foi possível ler o frame {frame_number}")
                    continue
                
                # Save frame to temporary file
                temp_dir = tempfile.gettempdir()
                frame_filename = f"frame_{i+1:03d}.jpg"
                frame_path = os.path.join(temp_dir, frame_filename)
                
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                
                logger.info(f"Frame {i+1}/{num_frames} extraído: {frame_path}")
            
            # Release video
            video.release()
            
            logger.info(f"Extração concluída: {len(frame_paths)} frames extraídos")
            return frame_paths
            
        except Exception as e:
            logger.error(f"Erro ao extrair frames: {e}", exc_info=True)
            return None
    
    def cleanup_files(self, file_paths: List[str]):
        """
        Remove temporary files
        
        Args:
            file_paths: List of file paths to remove
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Arquivo temporário removido: {file_path}")
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo {file_path}: {e}")
