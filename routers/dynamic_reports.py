"""
Router para Generación de Reportes Dinámicos con NLP
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.dynamic_reports_nlp import report_generator

router = APIRouter(prefix="/api/reports", tags=["Dynamic Reports"])


# Modelos Pydantic
class ReportRequest(BaseModel):
    query: str  # Consulta en lenguaje natural
    audio_transcript: Optional[str] = None  # Si viene de voz
    user_id: Optional[str] = None


class ReportExportRequest(BaseModel):
    report_id: str
    format: str  # 'excel', 'pdf', 'word'


# ============= ENDPOINTS =============

@router.post("/generate")
async def generate_dynamic_report(request: ReportRequest):
    """
    Genera un reporte dinámico a partir de una consulta en lenguaje natural
    
    **Ejemplos de consultas:**
    ```
    - "Quiero ver cuántos trámites completados hay este mes"
    - "Muéstrame las políticas más utilizadas"
    - "Dame un reporte de trámites rechazados en Excel"
    - "Cuál es el promedio de trámites por día"
    - "Lista los 10 trámites más recientes"
    ```
    
    **Request:**
    ```json
    {
        "query": "Quiero ver cuántos trámites completados hay este mes",
        "user_id": "user-123"
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "query": "...",
        "specification": {
            "fields": ["tramites"],
            "operation": "count",
            "filters": {"estado": "completado", "periodo": "mes"},
            "format": "html"
        },
        "data": {"count": 42, "entity": "tramites"},
        "summary": "Se encontraron 42 trámites que cumplen los criterios."
    }
    ```
    """
    try:
        # Usar transcripción de audio si está disponible
        query = request.audio_transcript or request.query
        
        # Generar reporte
        result = report_generator.generate_report(query)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")


@router.get("/examples")
async def get_query_examples():
    """
    Obtiene ejemplos de consultas válidas
    """
    return {
        'success': True,
        'examples': [
            {
                'category': 'Conteo',
                'queries': [
                    "¿Cuántos trámites completados hay?",
                    "Número total de políticas activas",
                    "Cantidad de trámites en proceso este mes"
                ]
            },
            {
                'category': 'Listado',
                'queries': [
                    "Muéstrame todos los trámites rechazados",
                    "Lista las políticas más utilizadas",
                    "Ver trámites de esta semana"
                ]
            },
            {
                'category': 'Estadísticas',
                'queries': [
                    "Promedio de trámites por día",
                    "Cuál es la política más usada",
                    "Tiempo promedio de procesamiento"
                ]
            },
            {
                'category': 'Con formato',
                'queries': [
                    "Dame un reporte en Excel de trámites completados",
                    "Exporta a PDF los trámites de hoy",
                    "Genera un documento Word con el resumen mensual"
                ]
            },
            {
                'category': 'Con filtros',
                'queries': [
                    "Top 10 trámites más recientes",
                    "Trámites completados ordenados por fecha",
                    "Primeros 5 usuarios más activos"
                ]
            }
        ],
        'tips': [
            "Puedes combinar filtros: 'trámites completados de esta semana en Excel'",
            "Usa palabras como 'cuántos', 'lista', 'promedio' para operaciones",
            "Especifica el formato: 'en Excel', 'en PDF', 'en Word'",
            "Puedes pedir ordenamiento: 'ordenado por fecha'",
            "Usa 'top N' o 'primeros N' para limitar resultados"
        ]
    }


@router.post("/parse-query")
async def parse_query_only(query: str):
    """
    Solo parsea la consulta sin generar el reporte (útil para validar)
    
    **Ejemplo:**
    ```
    POST /api/reports/parse-query?query=Cuántos%20trámites%20completados
    ```
    """
    try:
        spec = report_generator.parser.parse_query(query)
        
        return {
            'success': True,
            'original_query': query,
            'parsed_specification': spec,
            'explanation': {
                'fields': f"Se buscarán datos de: {', '.join(spec['fields'])}",
                'operation': f"Se realizará la operación: {spec['operation']}",
                'filters': f"Con {len(spec['filters'])} filtro(s) aplicado(s)" if spec['filters'] else "Sin filtros",
                'format': f"Formato de salida: {spec['format']}"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al parsear consulta: {str(e)}")


@router.post("/voice-query")
async def process_voice_query(audio_transcript: str, user_id: Optional[str] = None):
    """
    Procesa una consulta desde audio transcrito
    
    **Ejemplo:**
    ```
    POST /api/reports/voice-query?audio_transcript=muéstrame%20los%20trámites%20de%20hoy
    ```
    """
    try:
        result = report_generator.generate_report(audio_transcript)
        
        return {
            **result,
            'source': 'voice',
            'transcript': audio_transcript
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar consulta de voz: {str(e)}")


@router.get("/supported-fields")
async def get_supported_fields():
    """
    Lista los campos que se pueden consultar
    """
    return {
        'success': True,
        'supported_fields': [
            {
                'field': 'tramites',
                'keywords': ['trámite', 'trámites', 'solicitud', 'solicitudes'],
                'filters': ['estado', 'fecha', 'política']
            },
            {
                'field': 'politicas',
                'keywords': ['política', 'políticas'],
                'filters': ['activa', 'nombre']
            },
            {
                'field': 'usuarios',
                'keywords': ['usuario', 'cliente', 'funcionario'],
                'filters': ['rol', 'departamento']
            },
            {
                'field': 'departamentos',
                'keywords': ['departamento', 'área'],
                'filters': ['activo']
            },
            {
                'field': 'documentos',
                'keywords': ['documento', 'archivo'],
                'filters': ['tipo', 'estado']
            }
        ],
        'supported_operations': [
            {'operation': 'count', 'keywords': ['cuántos', 'cantidad', 'número']},
            {'operation': 'list', 'keywords': ['lista', 'muestra', 'ver']},
            {'operation': 'average', 'keywords': ['promedio', 'media']},
            {'operation': 'max', 'keywords': ['máximo', 'mayor']},
            {'operation': 'min', 'keywords': ['mínimo', 'menor']}
        ],
        'supported_formats': ['html', 'excel', 'pdf', 'word', 'json']
    }
