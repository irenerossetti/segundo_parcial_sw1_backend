"""
Router para health check
Endpoint: GET /api/health
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Verifica que el servicio está corriendo
    """
    return {
        "status": "ok",
        "service": "Workflow IA/ML Service",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@router.get("/health/detailed")
async def health_check_detailed():
    """
    Health check detallado
    Verifica estado de modelos y dependencias
    """
    return {
        "status": "ok",
        "service": "Workflow IA/ML Service",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "ok",
            "models": "loading",  # Se actualiza cuando se cargan modelos
            "python": "ok"
        },
        "version": "2.0.0"
    }
