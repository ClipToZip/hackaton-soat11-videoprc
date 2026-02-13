"""
Video Entity
Representa um vídeo no domínio da aplicação
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class VideoEntity(BaseModel):
    """Entidade de vídeo"""
    model_config = ConfigDict(from_attributes=True)

    video_id: str
    user_id: str
    data_video_up: datetime
    status: int  # 1=aguardando, 2=processando, 3=finalizado, 4=erro
    video_name: Optional[str] = None
    zip_name: Optional[str] = None
    descricao: Optional[str] = None
    titulo: Optional[str] = None
    metadados: Optional[dict] = None
    path: Optional[str] = None  # Path no S3 (antigo campo)
