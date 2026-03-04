"""
Repository Port
Interface para acesso ao repositório de dados
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from src.domain.entities.video_entity import VideoEntity
from src.domain.entities.user_entity import UserEntity


class VideoRepositoryPort(ABC):
    """Port (interface) para repositório de vídeos"""
    
    @abstractmethod
    def get_video_with_user(self, video_id: str) -> Optional[Tuple[VideoEntity, UserEntity]]:
        """
        Busca vídeo e usuário pelo ID do vídeo
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Tupla com (VideoEntity, UserEntity) ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def update_video_status(self, video_id: str, status: int, zip_name: Optional[str] = None) -> bool:
        """
        Atualiza o status do vídeo
        
        Args:
            video_id: ID do vídeo
            status: Novo status (1=aguardando, 2=processando, 3=finalizado, 4=erro)
            zip_name: Nome do arquivo ZIP no S3 (opcional)
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        pass
