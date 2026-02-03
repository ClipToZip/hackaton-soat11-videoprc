"""
User Entity
Representa um usuário no domínio da aplicação
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserEntity(BaseModel):
    """Entidade de usuário"""
    user_id: str
    name: Optional[str] = None
    email: EmailStr
    password_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True
