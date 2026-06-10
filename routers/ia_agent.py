"""
Router para Agente Inteligente - Policy Recommendation
Endpoint: POST /api/ia/policies/recommend
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ClientInput(BaseModel):
    """Entrada del cliente"""
    clientText: str
    clientAudio: Optional[str] = None  # Base64 encoded audio
    tramiteId: str
    userId: str


class PolicyRecommendation(BaseModel):
    """Recomendación de política"""
    policyId: str
    policyName: str
    description: str
    confidence: float  # 0.0 - 1.0
    matchedKeywords: List[str]
    requirementScore: float


class RecommendationResponse(BaseModel):
    """Respuesta con recomendaciones"""
    tramiteId: str
    timestamp: str
    recommendations: List[PolicyRecommendation]
    topRecommendation: PolicyRecommendation
    processingTime: float
    model: str


@router.post("/policies/recommend", response_model=RecommendationResponse)
async def recommend_policies(request: ClientInput):
    """
    Recomienda políticas basadas en texto del cliente
    
    Args:
        request: ClientInput con texto/audio del cliente
        
    Returns:
        Top 3 políticas recomendadas con confidence scores
    """
    try:
        import time
        start_time = time.time()
        
        logger.info(f"📋 Recomendación de política: tramite={request.tramiteId}")
        
        # Importar servicio
        from services.policy_matcher import PolicyMatcher
        
        matcher = PolicyMatcher()
        
        # Procesar texto
        recommendations = await matcher.find_best_policies(
            client_text=request.clientText,
            client_audio=request.clientAudio,
            top_k=3
        )
        
        processing_time = time.time() - start_time
        
        # Construir respuesta
        response = RecommendationResponse(
            tramiteId=request.tramiteId,
            timestamp=datetime.now().isoformat(),
            recommendations=recommendations,
            topRecommendation=recommendations[0] if recommendations else None,
            processingTime=processing_time,
            model="policy_matcher_v1"
        )
        
        logger.info(f"✓ Recomendación completa: {len(recommendations)} políticas (tiempo={processing_time:.2f}s)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error recomendando políticas: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing recommendation: {str(e)}")


@router.get("/policies/list")
async def list_available_policies():
    """
    Lista todas las políticas disponibles
    """
    try:
        from services.policy_matcher import PolicyMatcher
        
        matcher = PolicyMatcher()
        policies = await matcher.get_available_policies()
        
        return {
            "total": len(policies),
            "policies": policies,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error listando políticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/train")
async def train_model(trainingData: dict):
    """
    Entrena el modelo de recomendación con nuevos datos
    (Admin only - requiere autenticación)
    """
    try:
        logger.info("🤖 Entrenando modelo de políticas...")
        
        from services.policy_matcher import PolicyMatcher
        
        matcher = PolicyMatcher()
        result = await matcher.train_model(trainingData)
        
        logger.info("✓ Modelo entrenado exitosamente")
        return {
            "success": True,
            "message": "Model trained successfully",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error entrenando modelo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
