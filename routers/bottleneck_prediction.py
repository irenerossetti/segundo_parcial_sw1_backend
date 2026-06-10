"""
Router para Predicción de Cuellos de Botella con LSTM
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from services.bottleneck_lstm import bottleneck_predictor

router = APIRouter(prefix="/api/bottleneck", tags=["Bottleneck Prediction"])


# Modelos Pydantic
class HistoricalData(BaseModel):
    node_name: str
    historical_counts: List[float]  # Últimos N días
    n_days_ahead: int = 7


class TrainingRequest(BaseModel):
    n_days: int = 90
    n_nodes: int = 5
    epochs: int = 50


# ============= ENDPOINTS =============

@router.post("/train")
async def train_lstm_model(request: TrainingRequest):
    """
    Entrena el modelo LSTM con datos sintéticos
    
    **Ejemplo:**
    ```json
    {
        "n_days": 90,
        "n_nodes": 5,
        "epochs": 50
    }
    ```
    """
    try:
        # Generar datos sintéticos
        df = bottleneck_predictor.generate_synthetic_time_series(
            n_days=request.n_days,
            n_nodes=request.n_nodes
        )
        
        # Entrenar modelo
        metrics = bottleneck_predictor.train(
            df=df,
            epochs=request.epochs
        )
        
        return {
            'success': True,
            'message': 'Modelo LSTM entrenado exitosamente',
            'metrics': metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al entrenar: {str(e)}")


@router.post("/predict")
async def predict_bottlenecks(data: HistoricalData):
    """
    Predice cuellos de botella para los próximos N días
    
    **Ejemplo:**
    ```json
    {
        "node_name": "Validación Inicial",
        "historical_counts": [12, 15, 18, 14, 20, 22, 19],
        "n_days_ahead": 7
    }
    ```
    
    **Respuesta:**
    ```json
    {
        "node_name": "Validación Inicial",
        "predictions": [21, 23, 25, 24, 26, 28, 27],
        "risk_analysis": {
            "risk_level": "HIGH",
            "risk_days": [...],
            "recommendations": [...]
        }
    }
    ```
    """
    try:
        if not bottleneck_predictor.is_trained:
            # Auto-entrenar si no está entrenado
            df = bottleneck_predictor.generate_synthetic_time_series()
            bottleneck_predictor.train(df, epochs=30)
        
        # Predecir próximos días
        predictions = bottleneck_predictor.predict_next_days(
            historical_data=data.historical_counts,
            n_days_ahead=data.n_days_ahead
        )
        
        # Analizar riesgo
        risk_analysis = bottleneck_predictor.detect_bottleneck_risk(predictions)
        
        return {
            'success': True,
            'node_name': data.node_name,
            'historical_data': {
                'last_days': data.historical_counts[-7:],
                'average': sum(data.historical_counts) / len(data.historical_counts)
            },
            'predictions': predictions,
            'forecast_days': data.n_days_ahead,
            'risk_analysis': risk_analysis
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@router.get("/status")
async def get_model_status():
    """
    Obtiene estado del modelo LSTM
    """
    return {
        'success': True,
        'is_trained': bottleneck_predictor.is_trained,
        'sequence_length': bottleneck_predictor.sequence_length,
        'nodes_configured': len(bottleneck_predictor.node_names),
        'node_names': bottleneck_predictor.node_names
    }


@router.post("/analyze-workflow")
async def analyze_workflow_bottlenecks(tramite_id: str):
    """
    Analiza todos los nodos de un workflow y predice cuellos de botella
    
    **Ejemplo:**
    ```
    POST /api/bottleneck/analyze-workflow?tramite_id=TRM-001
    ```
    """
    try:
        # En producción, obtener datos reales de MongoDB
        # Por ahora, simulación
        
        nodes = [
            {'name': 'Validación Inicial', 'historical': [12, 15, 18, 14, 20, 22, 19, 21, 23, 20]},
            {'name': 'Análisis Técnico', 'historical': [8, 10, 12, 11, 13, 15, 14, 16, 18, 17]},
            {'name': 'Aprobación Legal', 'historical': [5, 6, 8, 7, 9, 11, 10, 12, 14, 13]},
            {'name': 'Firma Digital', 'historical': [3, 4, 5, 4, 6, 7, 6, 8, 9, 8]}
        ]
        
        if not bottleneck_predictor.is_trained:
            df = bottleneck_predictor.generate_synthetic_time_series()
            bottleneck_predictor.train(df, epochs=30)
        
        results = []
        
        for node in nodes:
            predictions = bottleneck_predictor.predict_next_days(
                historical_data=node['historical'],
                n_days_ahead=7
            )
            
            risk_analysis = bottleneck_predictor.detect_bottleneck_risk(predictions)
            
            results.append({
                'node_name': node['name'],
                'current_count': node['historical'][-1],
                'predictions': predictions,
                'risk_level': risk_analysis['risk_level'],
                'risk_days': len(risk_analysis['risk_days']),
                'recommendations': risk_analysis['recommendations'][:2]  # Top 2
            })
        
        # Ordenar por riesgo
        risk_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        results.sort(key=lambda x: risk_order.get(x['risk_level'], 0), reverse=True)
        
        # Resumen general
        critical_nodes = [r for r in results if r['risk_level'] in ['CRITICAL', 'HIGH']]
        
        return {
            'success': True,
            'tramite_id': tramite_id,
            'analysis_date': '2026-06-09',
            'nodes_analyzed': len(results),
            'critical_nodes_count': len(critical_nodes),
            'overall_risk': critical_nodes[0]['risk_level'] if critical_nodes else 'LOW',
            'nodes': results,
            'summary': {
                'message': f"Se detectaron {len(critical_nodes)} nodos con riesgo alto/crítico" if critical_nodes else "Flujo normal en todos los nodos",
                'action_required': len(critical_nodes) > 0
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")
