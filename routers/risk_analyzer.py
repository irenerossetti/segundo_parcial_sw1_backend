"""
Router para Risk Analyzer - Análisis de Riesgo
Endpoint: POST /api/riesgo/analyze
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TramiteData(BaseModel):
    """Datos del trámite para análisis"""
    tramiteId: str
    clientName: str
    policyType: str
    documents: List[str]
    clientHistory: Optional[Dict] = None
    additionalInfo: Optional[Dict] = None


class RiskFactor(BaseModel):
    """Factor de riesgo identificado"""
    name: str
    category: str  # DOCUMENTATION, CLIENT, POLICY, TIMELINE, etc
    riskLevel: str  # LOW, MEDIUM, HIGH, CRITICAL
    score: float  # 0-100
    description: str
    recommendation: str


class RiskAnalysisResponse(BaseModel):
    """Respuesta del análisis de riesgo"""
    tramiteId: str
    overallRiskScore: float  # 0-100
    overallRiskLevel: str  # LOW, MEDIUM, HIGH, CRITICAL
    riskFactors: List[RiskFactor]
    recommendations: List[str]
    approvalProbability: float  # 0-1
    estimatedResolutionDays: int
    timestamp: str


@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_risk(request: TramiteData):
    """
    Analiza riesgo de un trámite
    
    Args:
        request: Datos del trámite
        
    Returns:
        Análisis detallado de riesgo
    """
    try:
        logger.info(f"🔴 Analizando riesgo: tramite={request.tramiteId}, policy={request.policyType}")
        
        from services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        
        # Realizar análisis
        analysis = await analyzer.analyze_tramite(
            tramite_id=request.tramiteId,
            client_name=request.clientName,
            policy_type=request.policyType,
            documents=request.documents,
            client_history=request.clientHistory,
            additional_info=request.additionalInfo
        )
        
        response = RiskAnalysisResponse(
            tramiteId=request.tramiteId,
            overallRiskScore=analysis["overall_score"],
            overallRiskLevel=analysis["overall_level"],
            riskFactors=analysis["factors"],
            recommendations=analysis["recommendations"],
            approvalProbability=analysis["approval_probability"],
            estimatedResolutionDays=analysis["estimated_days"],
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✓ Análisis completado: riesgo={response.overallRiskLevel} (score={response.overallRiskScore})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error analizando riesgo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-analyze")
async def analyze_multiple(tramites: List[TramiteData]):
    """
    Analiza riesgo de múltiples trámites en paralelo
    """
    try:
        logger.info(f"📊 Analizando {len(tramites)} trámites...")
        
        from services.risk_analyzer import RiskAnalyzer
        import asyncio
        
        analyzer = RiskAnalyzer()
        
        # Analizar en paralelo
        tasks = [
            analyzer.analyze_tramite(
                tramite_id=t.tramiteId,
                client_name=t.clientName,
                policy_type=t.policyType,
                documents=t.documents
            )
            for t in tramites
        ]
        
        results = await asyncio.gather(*tasks)
        
        logger.info(f"✓ Análisis completado para {len(results)} trámites")
        
        return {
            "total": len(results),
            "analyses": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en análisis múltiple: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-categories")
async def get_risk_categories():
    """
    Lista categorías de riesgo disponibles
    """
    return {
        "categories": [
            {
                "name": "DOCUMENTATION",
                "description": "Riesgos relacionados con documentación faltante o inválida"
            },
            {
                "name": "CLIENT",
                "description": "Riesgos en datos o historial del cliente"
            },
            {
                "name": "POLICY",
                "description": "Riesgos en políticas y regulaciones"
            },
            {
                "name": "TIMELINE",
                "description": "Riesgos relacionados con plazos"
            },
            {
                "name": "COMPLIANCE",
                "description": "Riesgos de cumplimiento normativo"
            }
        ]
    }


@router.post("/predict-approval")
async def predict_approval(request: TramiteData):
    """
    Predice probabilidad de aprobación
    """
    try:
        logger.info(f"🎯 Prediciendo aprobación: {request.tramiteId}")
        
        from services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        prediction = await analyzer.predict_approval(request.dict())
        
        return {
            "tramiteId": request.tramiteId,
            "approvalProbability": prediction["probability"],
            "approvalLikelihood": prediction["likelihood"],  # VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH
            "topRisks": prediction["top_risks"],
            "topStrengths": prediction["top_strengths"],
            "suggestedActions": prediction["suggested_actions"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error prediciendo aprobación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor/{tramiteId}")
async def monitor_tramite(tramiteId: str):
    """
    Inicia monitoreo de riesgo en tiempo real para un trámite
    """
    try:
        logger.info(f"👁️ Iniciando monitoreo: {tramiteId}")
        
        from services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        result = await analyzer.start_monitoring(tramiteId)
        
        return {
            "tramiteId": tramiteId,
            "status": "MONITORING",
            "monitoringId": result["id"],
            "checkInterval": result["interval"],
            "alertThreshold": result["threshold"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error iniciando monitoreo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
