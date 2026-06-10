"""
Router para Agente Inteligente de Asignación de Políticas
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.intelligent_agent import conversation_manager, IntelligentPolicyAgent

router = APIRouter(prefix="/api/agent", tags=["Intelligent Agent"])

# Modelos Pydantic
class ClientRequest(BaseModel):
    text: str
    audio_transcript: Optional[str] = None
    user_id: Optional[str] = None


class ConversationMessage(BaseModel):
    user_id: str
    message: str
    audio_transcript: Optional[str] = None


class DocumentValidation(BaseModel):
    category: str
    provided_documents: List[str]


# ============= ENDPOINTS =============

@router.post("/analyze-request")
async def analyze_client_request(request: ClientRequest):
    """
    Analiza la solicitud del cliente y sugiere política apropiada
    
    **Ejemplo:**
    ```json
    {
        "text": "Necesito solicitar un préstamo personal urgente",
        "user_id": "user-123"
    }
    ```
    """
    try:
        agent = IntelligentPolicyAgent()
        result = agent.analyze_client_request(
            text=request.text,
            audio_transcript=request.audio_transcript
        )
        
        return {
            "success": True,
            "analysis": result,
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar solicitud: {str(e)}")


@router.post("/conversation/start")
async def start_conversation(user_id: str):
    """
    Inicia una conversación con el agente inteligente
    
    **Retorna:** Saludo inicial y sugerencias
    """
    try:
        result = conversation_manager.start_conversation(user_id)
        
        return {
            "success": True,
            "conversation": result,
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar conversación: {str(e)}")


@router.post("/conversation/message")
async def process_conversation_message(msg: ConversationMessage):
    """
    Procesa un mensaje en la conversación y retorna respuesta del agente
    
    **Ejemplo:**
    ```json
    {
        "user_id": "user-123",
        "message": "Necesito instalar medidor de luz",
        "audio_transcript": null
    }
    ```
    """
    try:
        result = conversation_manager.process_message(
            user_id=msg.user_id,
            message=msg.message,
            audio_transcript=msg.audio_transcript
        )
        
        return {
            "success": True,
            "conversation": result,
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar mensaje: {str(e)}")


@router.get("/conversation/history/{user_id}")
async def get_conversation_history(user_id: str):
    """
    Obtiene el historial de conversación de un usuario
    """
    try:
        history = conversation_manager.get_conversation_history(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "history": history,
            "total_messages": len(history),
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")


@router.post("/validate-requirements")
async def validate_requirements(validation: DocumentValidation):
    """
    Valida si el cliente tiene todos los documentos necesarios
    
    **Ejemplo:**
    ```json
    {
        "category": "CREDITO_BANCARIO",
        "provided_documents": ["identificación", "comprobante ingresos"]
    }
    ```
    """
    try:
        agent = IntelligentPolicyAgent()
        result = agent.validate_requirements(
            category=validation.category,
            provided_docs=validation.provided_documents
        )
        
        return {
            "success": True,
            "validation": result,
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar requisitos: {str(e)}")


@router.get("/policy-categories")
async def get_policy_categories():
    """
    Lista todas las categorías de políticas disponibles
    """
    try:
        agent = IntelligentPolicyAgent()
        
        categories = []
        for category, config in agent.policy_keywords.items():
            categories.append({
                "id": category,
                "name": category.replace("_", " ").title(),
                "keywords": config["keywords"],
                "required_documents": config["requires_docs"],
                "default_priority": config["priority_default"]
            })
        
        return {
            "success": True,
            "categories": categories,
            "total": len(categories),
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")


@router.post("/suggest-priority")
async def suggest_priority(text: str):
    """
    Sugiere prioridad basada en el texto de la solicitud
    """
    try:
        agent = IntelligentPolicyAgent()
        priority = agent.suggest_priority(text)
        
        return {
            "success": True,
            "text": text,
            "suggested_priority": priority,
            "timestamp": "2026-06-09T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sugerir prioridad: {str(e)}")
