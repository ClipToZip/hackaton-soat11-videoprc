"""
Video Repository Implementation
Implementação do repositório de vídeos usando PostgreSQL
"""
import logging
from typing import Optional, Tuple
from datetime import datetime
import json
from psycopg2.extras import RealDictCursor
from src.application.ports.repository_port import VideoRepositoryPort
from src.domain.entities.video_entity import VideoEntity
from src.domain.entities.user_entity import UserEntity
from src.adapters.output.persistence.database_connection import DatabaseConnection

logger = logging.getLogger(__name__)


class VideoRepository(VideoRepositoryPort):
    """Implementação do repositório de vídeos com PostgreSQL"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa o repositório
        
        Args:
            db_connection: Gerenciador de conexão com banco de dados
        """
        self.db_connection = db_connection
        logger.info("VideoRepository inicializado")
    
    def get_video_with_user(self, video_id: str) -> Optional[Tuple[VideoEntity, UserEntity]]:
        """
        Busca vídeo e usuário pelo ID do vídeo
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Tupla com (VideoEntity, UserEntity) ou None se não encontrado
        """
        cursor = None
        try:
            connection = self.db_connection.get_connection()
            
            # Para operações de leitura, usar autocommit evita problemas com transações
            old_autocommit = connection.autocommit
            connection.autocommit = True
            
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    v.video_id, v.user_id, v.data_video_up, v.status,
                    v.video_name, v.zip_name, v.descricao, v.titulo, v.metadados,
                    u.user_id as u_user_id, u.name, u.email, 
                    u.password_hash, u.created_at
                FROM cliptozip.videos v
                INNER JOIN cliptozip."user" u ON v.user_id = u.user_id
                WHERE v.video_id = %s
            """
            
            cursor.execute(query, (video_id,))
            row = cursor.fetchone()
            
            # Restaurar autocommit original
            connection.autocommit = old_autocommit
            
            if not row:
                logger.warning(f"Vídeo não encontrado: {video_id}")
                return None
            
            # Criar entidade de vídeo
            video = VideoEntity(
                video_id=str(row['video_id']),
                user_id=str(row['user_id']),
                data_video_up=row['data_video_up'],
                status=row['status'],
                video_name=row['video_name'],
                zip_name=row['zip_name'],
                descricao=row['descricao'],
                titulo=row['titulo'],
                metadados=row['metadados']
            )
            
            # Criar entidade de usuário
            user = UserEntity(
                user_id=str(row['u_user_id']),
                name=row['name'],
                email=row['email'],
                password_hash=row['password_hash'],
                created_at=row['created_at']
            )
            
            logger.info(f"Vídeo e usuário recuperados com sucesso: {video_id}")
            return (video, user)
            
        except Exception as e:
            logger.error(f"Erro ao buscar vídeo e usuário: {e}", exc_info=True)
            # Reverter transação em caso de erro
            self.db_connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
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
        cursor = None
        try:
            connection = self.db_connection.get_connection()
            cursor = connection.cursor()
            
            if zip_name:
                query = """
                    UPDATE cliptozip.videos 
                    SET status = %s, zip_name = %s
                    WHERE video_id = %s
                """
                cursor.execute(query, (status, zip_name, video_id))
            else:
                query = """
                    UPDATE cliptozip.videos 
                    SET status = %s
                    WHERE video_id = %s
                """
                cursor.execute(query, (status, video_id))
            
            connection.commit()
            
            logger.info(f"Status do vídeo atualizado: {video_id} -> Status: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do vídeo: {e}", exc_info=True)
            # Reverter transação em caso de erro
            self.db_connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
