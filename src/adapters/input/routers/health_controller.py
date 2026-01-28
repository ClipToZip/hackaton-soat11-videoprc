"""
Health controller para verificar o status da aplicação.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Endpoint de healthcheck para EKS/Docker
    """
    return {
        "status": "healthy",
        "service": "video-processor"
    }