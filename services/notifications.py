"""
Notifications Service - Notificaciones y WebHooks
Maneja alertas en tiempo real y WebHooks externos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import aiohttp

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio de notificaciones en tiempo real"""
    
    def __init__(self):
        logger.info("📬 Inicializando NotificationService...")
        self.notifications_db = {}  # Simulación de BD
        self.rules_db = {}
        self.webhooks_db = {}
        self.user_preferences = {}
    
    async def get_user_notifications(self, user_id: str, limit: int = 20, 
                                    unread_only: bool = False) -> List[Dict]:
        """
        Obtiene notificaciones del usuario
        """
        try:
            logger.info(f"📬 Obteniendo notificaciones: usuario={user_id}")
            
            # Simulación de datos
            notifications = [
                {
                    "id": str(uuid.uuid4()),
                    "userId": user_id,
                    "type": "success",
                    "title": "Trámite Aprobado",
                    "message": "Tu trámite ha sido aprobado exitosamente",
                    "read": False,
                    "createdAt": datetime.now().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "userId": user_id,
                    "type": "warning",
                    "title": "Riesgo Detectado",
                    "message": "Se detectó riesgo medio en tu trámite",
                    "read": True,
                    "createdAt": (datetime.now() - __import__('datetime').timedelta(hours=2)).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "userId": user_id,
                    "type": "info",
                    "title": "Documento Requerido",
                    "message": "Por favor, sube el documento de identificación",
                    "read": False,
                    "createdAt": (datetime.now() - __import__('datetime').timedelta(days=1)).isoformat()
                }
            ]
            
            if unread_only:
                notifications = [n for n in notifications if not n["read"]]
            
            return notifications[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo notificaciones: {str(e)}")
            raise
    
    async def mark_read(self, notification_id: str) -> Dict:
        """
        Marca una notificación como leída
        """
        try:
            logger.info(f"✓ Marcando como leída: {notification_id}")
            
            # En BD real: actualizar status
            self.notifications_db[notification_id] = {"read": True}
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ Error marcando como leída: {str(e)}")
            raise
    
    async def create_rule(self, rule) -> Dict:
        """
        Crea una nueva regla de notificación
        """
        try:
            logger.info(f"📋 Creando regla: {rule.id}")
            
            self.rules_db[rule.id] = rule.dict()
            
            logger.info("✓ Regla creada")
            
            return {"ruleId": rule.id}
            
        except Exception as e:
            logger.error(f"❌ Error creando regla: {str(e)}")
            raise
    
    async def get_all_rules(self) -> List[Dict]:
        """
        Obtiene todas las reglas de notificación
        """
        try:
            logger.info("📋 Obteniendo reglas")
            
            # Retornar reglas predefinidas
            rules = [
                {
                    "id": "rule_high_risk",
                    "trigger": "high_risk",
                    "conditions": {"riskScore": {"gt": 75}},
                    "actions": ["email", "sms", "push"],
                    "enabled": True
                },
                {
                    "id": "rule_approval",
                    "trigger": "approval",
                    "conditions": {"status": "APPROVED"},
                    "actions": ["email", "push"],
                    "enabled": True
                },
                {
                    "id": "rule_rejection",
                    "trigger": "rejection",
                    "conditions": {"status": "REJECTED"},
                    "actions": ["email", "sms"],
                    "enabled": True
                }
            ]
            
            return rules
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo reglas: {str(e)}")
            raise
    
    async def register_webhook(self, config) -> str:
        """
        Registra un WebHook externo
        """
        try:
            logger.info(f"🔗 Registrando WebHook: {config.url}")
            
            webhook_id = str(uuid.uuid4())
            self.webhooks_db[webhook_id] = config.dict()
            
            logger.info(f"✓ WebHook registrado: {webhook_id}")
            
            return webhook_id
            
        except Exception as e:
            logger.error(f"❌ Error registrando WebHook: {str(e)}")
            raise
    
    async def get_all_webhooks(self) -> List[Dict]:
        """
        Lista todos los WebHooks registrados
        """
        try:
            logger.info("🔗 Listando WebHooks")
            
            webhooks = []
            for webhook_id, config in self.webhooks_db.items():
                webhooks.append({
                    "id": webhook_id,
                    **config
                })
            
            return webhooks
            
        except Exception as e:
            logger.error(f"❌ Error listando WebHooks: {str(e)}")
            raise
    
    async def send_notification(self, notification) -> Dict:
        """
        Envía una notificación
        """
        try:
            logger.info(f"📤 Enviando notificación: usuario={notification.userId}")
            
            # Guardar en BD
            self.notifications_db[notification.id] = notification.dict()
            
            # En producción: Enviar por email, SMS, push, etc.
            await self._send_by_channels(notification)
            
            logger.info("✓ Notificación enviada")
            
            return {"notificationId": notification.id}
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {str(e)}")
            raise
    
    async def send_bulk_notifications(self, notifications: List) -> List[str]:
        """
        Envía múltiples notificaciones
        """
        try:
            logger.info(f"📤 Enviando {len(notifications)} notificaciones")
            
            results = []
            for notification in notifications:
                try:
                    result = await self.send_notification(notification)
                    results.append(result["notificationId"])
                except Exception as e:
                    logger.error(f"❌ Error enviando notificación {notification.id}: {str(e)}")
            
            logger.info(f"✓ {len(results)} notificaciones enviadas")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en bulk send: {str(e)}")
            raise
    
    async def _send_by_channels(self, notification) -> None:
        """
        Envía notificación por múltiples canales
        """
        try:
            # Email
            if "email" in notification.type:
                await self._send_email(notification)
            
            # SMS
            if "sms" in notification.type:
                await self._send_sms(notification)
            
            # Push
            if "push" in notification.type:
                await self._send_push(notification)
            
            # WebHooks
            await self._trigger_webhooks(notification)
            
        except Exception as e:
            logger.error(f"❌ Error en canales de envío: {str(e)}")
    
    async def _send_email(self, notification) -> None:
        """Envía por email"""
        logger.info(f"📧 Enviando email: {notification.userId}")
        # Implementación: usar SMTP
    
    async def _send_sms(self, notification) -> None:
        """Envía SMS"""
        logger.info(f"📱 Enviando SMS: {notification.userId}")
        # Implementación: usar Twilio u otro proveedor
    
    async def _send_push(self, notification) -> None:
        """Envía push notification"""
        logger.info(f"🔔 Enviando push: {notification.userId}")
        # Implementación: usar Firebase, etc.
    
    async def _trigger_webhooks(self, notification) -> None:
        """Dispara WebHooks registrados"""
        try:
            logger.info("🔗 Disparando WebHooks")
            
            for webhook_id, config in self.webhooks_db.items():
                if config.get("active"):
                    async with aiohttp.ClientSession() as session:
                        try:
                            async with session.post(
                                config["url"],
                                json=notification.dict(),
                                headers=config.get("headers", {}),
                                timeout=10
                            ) as response:
                                logger.info(f"✓ WebHook disparado: {response.status}")
                        except Exception as e:
                            logger.error(f"❌ Error disparando WebHook {webhook_id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"❌ Error en trigger de WebHooks: {str(e)}")
    
    async def get_preferences(self, user_id: str) -> Dict:
        """
        Obtiene preferencias de notificación del usuario
        """
        try:
            logger.info(f"⚙️  Obteniendo preferencias: {user_id}")
            
            return self.user_preferences.get(user_id, {
                "email": True,
                "sms": False,
                "push": True,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00",
                "notification_frequency": "immediate"
            })
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo preferencias: {str(e)}")
            raise
    
    async def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """
        Actualiza preferencias de notificación
        """
        try:
            logger.info(f"⚙️  Actualizando preferencias: {user_id}")
            
            self.user_preferences[user_id] = preferences
            
            logger.info("✓ Preferencias actualizadas")
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ Error actualizando preferencias: {str(e)}")
            raise


# Instancia global
_notification_service = None


def get_notification_service() -> NotificationService:
    """Obtiene instancia singleton del NotificationService"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
