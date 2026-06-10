"""
Router para Analytics Dashboard - Métricas y visualizaciones
Endpoints: POST/GET /api/analytics/*
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class MetricsRequest(BaseModel):
    """Request para obtener métricas"""
    startDate: str  # ISO format
    endDate: str
    metrics: List[str]  # ["approvals", "rejections", "risk_scores", "processing_time"]
    groupBy: str = "day"  # day, week, month


class DashboardWidget(BaseModel):
    """Widget del dashboard"""
    id: str
    title: str
    type: str  # bar, line, pie, gauge, table
    data: Dict
    config: Optional[Dict] = None


class DashboardConfig(BaseModel):
    """Configuración del dashboard"""
    widgets: List[DashboardWidget]
    refreshInterval: int  # segundos
    theme: str = "light"


@router.get("/metrics")
async def get_metrics(
    start_date: str = Query(""),
    end_date: str = Query(""),
    metric_type: str = Query("all")
):
    """
    Obtiene métricas agregadas del sistema
    
    Métricas disponibles:
    - approvals: Número de aprobaciones
    - rejections: Número de rechazos
    - risk_scores: Distribución de scores de riesgo
    - processing_time: Tiempo promedio de procesamiento
    - policy_distribution: Distribución de políticas
    - client_satisfaction: Satisfacción del cliente
    """
    try:
        logger.info(f"📊 Obteniendo métricas: tipo={metric_type}")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        metrics = await service.get_metrics(
            start_date=start_date,
            end_date=end_date,
            metric_type=metric_type
        )
        
        return {
            "metrics": metrics,
            "generatedAt": datetime.now().isoformat(),
            "period": f"{start_date} to {end_date}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard(user_id: str, dashboard_type: str = "overview"):
    """
    Obtiene configuración del dashboard personalizado
    
    Tipos: overview, detailed, executive, custom
    """
    try:
        logger.info(f"📈 Cargando dashboard: type={dashboard_type}")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        dashboard = await service.get_dashboard(user_id, dashboard_type)
        
        return {
            "dashboard": dashboard,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error cargando dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/save")
async def save_dashboard(user_id: str, config: DashboardConfig):
    """
    Guarda configuración personalizada del dashboard
    """
    try:
        logger.info(f"💾 Guardando dashboard para usuario: {user_id}")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        result = await service.save_dashboard_config(user_id, config)
        
        logger.info("✓ Dashboard guardado")
        
        return {
            "success": True,
            "message": "Dashboard saved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error guardando dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trends(period_days: int = 30):
    """
    Obtiene tendencias de los últimos N días
    """
    try:
        logger.info(f"📈 Obteniendo tendencias: período={period_days} días")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        trends = await service.calculate_trends(period_days)
        
        return {
            "trends": trends,
            "periodDays": period_days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculando tendencias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_metrics():
    """
    Obtiene métricas de performance del sistema
    """
    try:
        logger.info("⚡ Calculando performance metrics")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        performance = await service.get_performance_metrics()
        
        return {
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-report")
async def export_analytics_report(format: str = "PDF"):
    """
    Exporta reporte analítico completo
    
    Formatos: PDF, XLSX, CSV
    """
    try:
        logger.info(f"📤 Exportando reporte: formato={format}")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        result = await service.export_report(format)
        
        return {
            "fileName": result["filename"],
            "downloadUrl": result["url"],
            "fileSize": result["size"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error exportando reporte: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpi")
async def get_kpi_metrics():
    """
    Obtiene KPIs principales del negocio
    """
    try:
        logger.info("🎯 Calculando KPIs")
        
        from services.analytics import AnalyticsService
        
        service = AnalyticsService()
        
        kpis = await service.calculate_kpis()
        
        return {
            "kpis": kpis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculando KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
