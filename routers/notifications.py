"""
Router para Notificaciones y WebHooks en tiempo real
Endpoints: POST/GET /api/notifications/*
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


class NotificationRule(BaseModel):
    """Regla para disparo de notificaciones"""
    id: str
    trigger: str  # "high_risk", "approval", "rejection", "milestone"
    conditions: Dict
    actions: List[str]  # ["email", "sms", "push", "webhook"]
    enabled: bool = True


class Notification(BaseModel):
    """Modelo de notificación"""
    id: str
    userId: str
    type: str  # "success", "warning", "error", "info"
    title: str
    message: str
    data: Optional[Dict] = None
    read: bool = False
    createdAt: str


class WebHookConfig(BaseModel):
    """Configuración de WebHook"""
    url: str
    events: List[str]  # ["tramite.created", "tramite.updated", "risk.analyzed"]
    active: bool = True
    headers: Optional[Dict] = None


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"📱 Cliente conectado: {user_id}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"📱 Cliente desconectado: {user_id}")
    
    async def broadcast_to_user(self, user_id: str, message: Dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"❌ Error enviando mensaje a {user_id}: {str(e)}")
                self.disconnect(user_id)
    
    async def broadcast(self, message: Dict):
        for websocket in self.active_connections.values():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error en broadcast: {str(e)}")


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(user_id: str, websocket: WebSocket):
    """
    WebSocket para notificaciones en tiempo real
    """
    try:
        await manager.connect(user_id, websocket)
        
        while True:
            # Esperar mensajes del cliente
            data = await websocket.receive_text()
            
            # Echo del cliente (heartbeat)
            await manager.broadcast_to_user(user_id, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"WebSocket desconectado: {user_id}")
    except Exception as e:
        logger.error(f"❌ Error en WebSocket: {str(e)}")
        manager.disconnect(user_id)


@router.get("/user/{user_id}")
async def get_notifications(user_id: str, limit: int = 20, unread_only: bool = False):
    """
    Obtiene notificaciones del usuario
    """
    try:
        logger.info(f"📬 Obteniendo notificaciones: usuario={user_id}, unread={unread_only}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        notifications = await service.get_user_notifications(user_id, limit, unread_only)
        
        return {
            "notifications": notifications,
            "total": len(notifications),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo notificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str):
    """
    Marca una notificación como leída
    """
    try:
        logger.info(f"✓ Marcando notificación como leída: {notification_id}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        await service.mark_read(notification_id)
        
        return {
            "success": True,
            "notificationId": notification_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error marcando notificación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/create")
async def create_notification_rule(rule: NotificationRule):
    """
    Crea una nueva regla de notificación
    """
    try:
        logger.info(f"📋 Creando regla de notificación: {rule.id}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        result = await service.create_rule(rule)
        
        logger.info("✓ Regla creada")
        
        return {
            "success": True,
            "ruleId": rule.id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error creando regla: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_notification_rules():
    """
    Obtiene todas las reglas de notificación
    """
    try:
        logger.info("📋 Obteniendo reglas de notificación")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        rules = await service.get_all_rules()
        
        return {
            "rules": rules,
            "total": len(rules),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo reglas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/register")
async def register_webhook(config: WebHookConfig):
    """
    Registra un WebHook externo
    """
    try:
        logger.info(f"🔗 Registrando WebHook: {config.url}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        webhook_id = await service.register_webhook(config)
        
        logger.info(f"✓ WebHook registrado: {webhook_id}")
        
        return {
            "success": True,
            "webhookId": webhook_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error registrando WebHook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks")
async def get_webhooks():
    """
    Lista todos los WebHooks registrados
    """
    try:
        logger.info("🔗 Listando WebHooks")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        webhooks = await service.get_all_webhooks()
        
        return {
            "webhooks": webhooks,
            "total": len(webhooks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error listando WebHooks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_notification(notification: Notification):
    """
    Envía una notificación manual
    """
    try:
        logger.info(f"📤 Enviando notificación: usuario={notification.userId}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        result = await service.send_notification(notification)
        
        return {
            "success": True,
            "notificationId": notification.id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando notificación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-send")
async def send_bulk_notifications(notifications: List[Notification]):
    """
    Envía múltiples notificaciones
    """
    try:
        logger.info(f"📤 Enviando {len(notifications)} notificaciones")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        results = await service.send_bulk_notifications(notifications)
        
        logger.info(f"✓ {len(results)} notificaciones enviadas")
        
        return {
            "success": True,
            "sent": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en bulk send: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}")
async def get_notification_preferences(user_id: str):
    """
    Obtiene preferencias de notificación del usuario
    """
    try:
        logger.info(f"⚙️  Obteniendo preferencias: {user_id}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        preferences = await service.get_preferences(user_id)
        
        return {
            "preferences": preferences,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo preferencias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{user_id}")
async def update_notification_preferences(user_id: str, preferences: Dict):
    """
    Actualiza preferencias de notificación
    """
    try:
        logger.info(f"⚙️  Actualizando preferencias: {user_id}")
        
        from services.notifications import NotificationService
        
        service = NotificationService()
        
        await service.update_preferences(user_id, preferences)
        
        logger.info("✓ Preferencias actualizadas")
        
        return {
            "success": True,
            "userId": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error actualizando preferencias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
