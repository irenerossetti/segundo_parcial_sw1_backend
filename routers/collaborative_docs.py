"""
Router para Edición Colaborativa de Documentos
Endpoints REST + WebSocket para colaboración en tiempo real
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import logging

from services.collaborative_editor import collaborative_editor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/collaborative")


# ========================================
# MODELOS PYDANTIC
# ========================================

class CreateDocumentRequest(BaseModel):
    doc_id: str
    content: str
    owner_id: str


class ApplyChangeRequest(BaseModel):
    doc_id: str
    user_id: str
    change_type: str  # insert, delete, replace
    position: Optional[int] = 0
    content: str


class UpdateCursorRequest(BaseModel):
    doc_id: str
    user_id: str
    position: int


# ========================================
# ENDPOINTS REST
# ========================================

@router.post("/create-document")
async def create_document(request: CreateDocumentRequest):
    """
    Crea un nuevo documento colaborativo
    """
    try:
        doc = collaborative_editor.create_document(
            doc_id=request.doc_id,
            content=request.content,
            owner_id=request.owner_id
        )
        
        return {
            'success': True,
            'document': doc.get_state(),
            'message': 'Documento colaborativo creado'
        }
    
    except Exception as e:
        logger.error(f"Error creando documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """
    Obtiene estado actual de un documento
    """
    state = collaborative_editor.get_document_state(doc_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return {
        'success': True,
        'document': state
    }


@router.post("/apply-change")
async def apply_change(request: ApplyChangeRequest):
    """
    Aplica un cambio al documento (alternativa a WebSocket)
    """
    try:
        result = collaborative_editor.apply_change(
            doc_id=request.doc_id,
            change_data=request.dict()
        )
        
        if result['success']:
            # Broadcast a otros usuarios (simulado)
            collaborative_editor.broadcast_change(
                doc_id=request.doc_id,
                change=result['change']
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error aplicando cambio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-cursor")
async def update_cursor(request: UpdateCursorRequest):
    """
    Actualiza posición del cursor de un usuario
    """
    result = collaborative_editor.update_cursor(
        doc_id=request.doc_id,
        user_id=request.user_id,
        position=request.position
    )
    
    return result


@router.get("/history/{doc_id}")
async def get_change_history(doc_id: str, limit: int = 50):
    """
    Obtiene historial de cambios de un documento
    """
    history = collaborative_editor.get_change_history(doc_id, limit)
    
    return {
        'success': True,
        'doc_id': doc_id,
        'history': history,
        'count': len(history)
    }


@router.post("/save-snapshot/{doc_id}")
async def save_snapshot(doc_id: str):
    """
    Guarda snapshot del documento actual
    """
    result = collaborative_editor.save_snapshot(doc_id)
    
    if not result['success']:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return result


@router.get("/active-documents")
async def get_active_documents():
    """
    Lista documentos con usuarios activos
    """
    active = collaborative_editor.get_active_documents()
    
    return {
        'success': True,
        'documents': active,
        'count': len(active)
    }


# ========================================
# WEBSOCKET ENDPOINT
# ========================================

@router.websocket("/ws/{doc_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str, user_id: str):
    """
    WebSocket para edición colaborativa en tiempo real
    
    Protocolo de mensajes:
    
    Cliente → Servidor:
    {
        "action": "join",
        "username": "Juan Pérez"
    }
    {
        "action": "change",
        "change_type": "insert",
        "position": 10,
        "content": "texto"
    }
    {
        "action": "cursor",
        "position": 25
    }
    {
        "action": "leave"
    }
    
    Servidor → Cliente:
    {
        "type": "welcome",
        "color": "#FF6B6B",
        "document": {...}
    }
    {
        "type": "change",
        "change": {...}
    }
    {
        "type": "cursor",
        "user_id": "...",
        "position": 25
    }
    {
        "type": "user_joined",
        "user": {...}
    }
    {
        "type": "user_left",
        "user_id": "..."
    }
    """
    await websocket.accept()
    logger.info(f"🔌 WebSocket conectado: user={user_id}, doc={doc_id}")
    
    try:
        # Esperar mensaje de join
        data = await websocket.receive_json()
        
        if data.get('action') != 'join':
            await websocket.send_json({
                'type': 'error',
                'message': 'Primer mensaje debe ser "join"'
            })
            await websocket.close()
            return
        
        username = data.get('username', f'Usuario {user_id[:8]}')
        
        # Unir al documento
        try:
            result = collaborative_editor.join_document(
                doc_id=doc_id,
                user_id=user_id,
                username=username,
                websocket=websocket
            )
            
            # Enviar bienvenida
            await websocket.send_json({
                'type': 'welcome',
                'color': result['color'],
                'document': result['document_state']
            })
            
            # Notificar a otros usuarios
            collaborative_editor.broadcast_change(
                doc_id=doc_id,
                change={
                    'type': 'user_joined',
                    'user': {
                        'user_id': user_id,
                        'username': username,
                        'color': result['color']
                    }
                },
                exclude_websocket=websocket
            )
        
        except ValueError as e:
            await websocket.send_json({
                'type': 'error',
                'message': str(e)
            })
            await websocket.close()
            return
        
        # Loop de mensajes
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            
            if action == 'change':
                # Aplicar cambio
                result = collaborative_editor.apply_change(
                    doc_id=doc_id,
                    change_data={
                        'user_id': user_id,
                        'change_type': data['change_type'],
                        'position': data.get('position', 0),
                        'content': data['content']
                    }
                )
                
                if result['success']:
                    # Broadcast a todos incluyendo emisor
                    await websocket.send_json({
                        'type': 'change_applied',
                        'change': result['change']
                    })
                    
                    collaborative_editor.broadcast_change(
                        doc_id=doc_id,
                        change=result['change'],
                        exclude_websocket=websocket
                    )
            
            elif action == 'cursor':
                # Actualizar cursor
                collaborative_editor.update_cursor(
                    doc_id=doc_id,
                    user_id=user_id,
                    position=data['position']
                )
                
                # Broadcast posición del cursor
                collaborative_editor.broadcast_change(
                    doc_id=doc_id,
                    change={
                        'type': 'cursor',
                        'user_id': user_id,
                        'position': data['position']
                    },
                    exclude_websocket=websocket
                )
            
            elif action == 'leave':
                break
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket desconectado: user={user_id}, doc={doc_id}")
    
    except Exception as e:
        logger.error(f"❌ Error en WebSocket: {e}")
    
    finally:
        # Limpiar al salir
        collaborative_editor.leave_document(doc_id, user_id, websocket)
        
        # Notificar a otros usuarios
        collaborative_editor.broadcast_change(
            doc_id=doc_id,
            change={
                'type': 'user_left',
                'user_id': user_id
            }
        )


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/health")
async def health_check():
    """Health check del servicio colaborativo"""
    active_docs = collaborative_editor.get_active_documents()
    
    return {
        'status': 'healthy',
        'service': 'Collaborative Editor',
        'active_documents': len(active_docs),
        'total_documents': len(collaborative_editor.documents)
    }
