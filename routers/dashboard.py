"""
Router para Dashboard Predictivo Avanzado
Endpoints para métricas, análisis y visualizaciones
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from services.predictive_dashboard import predictive_dashboard

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard")


# ========================================
# ENDPOINTS DE MÉTRICAS
# ========================================

@router.get("/overview")
async def get_overview():
    """
    Obtiene métricas generales del dashboard
    
    Retorna:
    - Total de trámites
    - Cambio vs periodo anterior
    - Tasa de éxito
    - Tiempo promedio
    - Satisfacción promedio
    """
    try:
        metrics = predictive_dashboard.get_overview_metrics()
        
        return {
            'success': True,
            'metrics': metrics
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/time-series")
async def get_time_series(days: int = Query(default=30, ge=7, le=90)):
    """
    Obtiene serie temporal de trámites
    
    Params:
    - days: Número de días (7-90, default: 30)
    
    Retorna datos para gráfica de líneas temporal
    """
    try:
        data = predictive_dashboard.get_time_series(days)
        
        return {
            'success': True,
            'time_series': data
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo time series: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions")
async def get_predictions(days_ahead: int = Query(default=7, ge=1, le=30)):
    """
    Genera predicciones para próximos días
    
    Params:
    - days_ahead: Días a predecir (1-30, default: 7)
    
    Retorna:
    - Predicciones
    - Banda de confianza
    - Tendencia
    """
    try:
        predictions = predictive_dashboard.get_predictions(days_ahead)
        
        return {
            'success': True,
            'predictions': predictions
        }
    
    except Exception as e:
        logger.error(f"Error generando predicciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/distribution")
async def get_distribution():
    """
    Obtiene distribución de trámites por estado
    
    Retorna datos para gráfica de torta/dona
    """
    try:
        distribution = predictive_dashboard.get_distribution_by_state()
        
        return {
            'success': True,
            'distribution': distribution
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo distribución: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processing-time")
async def get_processing_time():
    """
    Análisis de tiempos de procesamiento
    
    Retorna:
    - Promedio, mediana, min, max
    - Distribución (rápido/normal/lento)
    - Tendencia
    """
    try:
        analysis = predictive_dashboard.get_processing_time_analysis()
        
        return {
            'success': True,
            'processing_time': analysis
        }
    
    except Exception as e:
        logger.error(f"Error analizando tiempos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satisfaction")
async def get_satisfaction():
    """
    Tendencia de satisfacción de usuarios
    
    Retorna serie temporal con promedio móvil
    """
    try:
        satisfaction = predictive_dashboard.get_satisfaction_trend()
        
        return {
            'success': True,
            'satisfaction': satisfaction
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo satisfacción: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts():
    """
    Obtiene alertas de cuellos de botella
    
    Retorna lista de alertas con nivel (success/warning/danger)
    """
    try:
        alerts = predictive_dashboard.get_bottleneck_alerts()
        
        return {
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-performers")
async def get_top_performers():
    """
    Usuarios/departamentos con mejor desempeño
    
    Retorna top 5 con métricas
    """
    try:
        performers = predictive_dashboard.get_top_performers()
        
        return {
            'success': True,
            **performers
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo top performers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# ENDPOINT COMPLETO
# ========================================

@router.get("/complete")
async def get_complete_dashboard(days: int = Query(default=30, ge=7, le=90)):
    """
    Obtiene todos los datos del dashboard en una sola llamada
    
    Útil para cargar dashboard completo de una vez
    """
    try:
        return {
            'success': True,
            'timestamp': predictive_dashboard.historical_data[-1]['date'],
            'overview': predictive_dashboard.get_overview_metrics(),
            'time_series': predictive_dashboard.get_time_series(days),
            'predictions': predictive_dashboard.get_predictions(7),
            'distribution': predictive_dashboard.get_distribution_by_state(),
            'processing_time': predictive_dashboard.get_processing_time_analysis(),
            'satisfaction': predictive_dashboard.get_satisfaction_trend(),
            'alerts': predictive_dashboard.get_bottleneck_alerts(),
            'top_performers': predictive_dashboard.get_top_performers()
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo dashboard completo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/health")
async def health_check():
    """Health check del servicio de dashboard"""
    return {
        'status': 'healthy',
        'service': 'Predictive Dashboard',
        'data_points': len(predictive_dashboard.historical_data)
    }
