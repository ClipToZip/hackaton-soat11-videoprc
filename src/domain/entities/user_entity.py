"""
User Entity
Representa um usuário no domínio da aplicação
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserEntity(BaseModel):
    """Entidade de usuário"""
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    name: Optional[str] = None
    email: EmailStr
    password_hash: str
    created_at: datetime
