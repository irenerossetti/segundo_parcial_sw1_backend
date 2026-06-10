"""
Editor Colaborativo de Documentos en Tiempo Real
Permite a múltiples usuarios editar documentos simultáneamente con WebSocket
"""
from typing import Dict, List, Set, Optional
from datetime import datetime
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class DocumentChange:
    """Representa un cambio en el documento"""
    def __init__(self, 
                 change_id: str,
                 doc_id: str,
                 user_id: str,
                 change_type: str,
                 position: int,
                 content: str,
                 timestamp: str):
        self.change_id = change_id
        self.doc_id = doc_id
        self.user_id = user_id
        self.change_type = change_type  # insert, delete, replace
        self.position = position
        self.content = content
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict:
        return {
            'change_id': self.change_id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'change_type': self.change_type,
            'position': self.position,
            'content': self.content,
            'timestamp': self.timestamp
        }


class ActiveUser:
    """Usuario activo editando un documento"""
    def __init__(self, user_id: str, username: str, color: str):
        self.user_id = user_id
        self.username = username
        self.color = color  # Color del cursor
        self.cursor_position = 0
        self.last_seen = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'color': self.color,
            'cursor_position': self.cursor_position,
            'last_seen': self.last_seen.isoformat()
        }


class CollaborativeDocument:
    """Documento con edición colaborativa"""
    def __init__(self, doc_id: str, content: str, owner_id: str):
        self.doc_id = doc_id
        self.content = content
        self.owner_id = owner_id
        self.version = 1
        self.active_users: Dict[str, ActiveUser] = {}
        self.change_history: List[DocumentChange] = []
        self.created_at = datetime.now()
        self.last_modified = datetime.now()
    
    def add_user(self, user_id: str, username: str) -> str:
        """Agrega usuario activo y retorna color asignado"""
        if user_id in self.active_users:
            return self.active_users[user_id].color
        
        # Asignar color único
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
        used_colors = {u.color for u in self.active_users.values()}
        available = [c for c in colors if c not in used_colors]
        color = available[0] if available else colors[0]
        
        self.active_users[user_id] = ActiveUser(user_id, username, color)
        logger.info(f"✓ Usuario {username} ({user_id}) unido a documento {self.doc_id}")
        
        return color
    
    def remove_user(self, user_id: str):
        """Remueve usuario activo"""
        if user_id in self.active_users:
            username = self.active_users[user_id].username
            del self.active_users[user_id]
            logger.info(f"✓ Usuario {username} ({user_id}) salió del documento {self.doc_id}")
    
    def update_cursor(self, user_id: str, position: int):
        """Actualiza posición del cursor de un usuario"""
        if user_id in self.active_users:
            self.active_users[user_id].cursor_position = position
            self.active_users[user_id].last_seen = datetime.now()
    
    def apply_change(self, change: DocumentChange) -> bool:
        """Aplica un cambio al documento"""
        try:
            if change.change_type == 'insert':
                # Insertar contenido en posición
                self.content = (self.content[:change.position] + 
                              change.content + 
                              self.content[change.position:])
            
            elif change.change_type == 'delete':
                # Eliminar contenido desde posición
                length = int(change.content)  # content contiene la longitud
                self.content = (self.content[:change.position] + 
                              self.content[change.position + length:])
            
            elif change.change_type == 'replace':
                # Reemplazar todo el contenido
                self.content = change.content
            
            self.change_history.append(change)
            self.version += 1
            self.last_modified = datetime.now()
            
            logger.info(f"✓ Cambio aplicado al documento {self.doc_id}: {change.change_type}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error aplicando cambio: {e}")
            return False
    
    def get_state(self) -> Dict:
        """Retorna estado actual del documento"""
        return {
            'doc_id': self.doc_id,
            'content': self.content,
            'version': self.version,
            'owner_id': self.owner_id,
            'active_users': [u.to_dict() for u in self.active_users.values()],
            'last_modified': self.last_modified.isoformat(),
            'change_count': len(self.change_history)
        }


class CollaborativeEditorService:
    """
    Servicio de edición colaborativa
    Maneja documentos, usuarios y cambios en tiempo real
    """
    
    def __init__(self):
        self.documents: Dict[str, CollaborativeDocument] = {}
        # Mapa: doc_id -> Set[websocket connections]
        self.connections: Dict[str, Set] = {}
    
    def create_document(self, doc_id: str, content: str, owner_id: str) -> CollaborativeDocument:
        """Crea nuevo documento colaborativo"""
        if doc_id in self.documents:
            return self.documents[doc_id]
        
        doc = CollaborativeDocument(doc_id, content, owner_id)
        self.documents[doc_id] = doc
        self.connections[doc_id] = set()
        
        logger.info(f"✓ Documento colaborativo creado: {doc_id}")
        return doc
    
    def get_document(self, doc_id: str) -> Optional[CollaborativeDocument]:
        """Obtiene documento existente"""
        return self.documents.get(doc_id)
    
    def join_document(self, doc_id: str, user_id: str, username: str, websocket) -> Dict:
        """Usuario se une a un documento"""
        doc = self.documents.get(doc_id)
        if not doc:
            raise ValueError(f"Documento {doc_id} no existe")
        
        # Agregar usuario
        color = doc.add_user(user_id, username)
        
        # Agregar conexión WebSocket
        self.connections[doc_id].add(websocket)
        
        return {
            'success': True,
            'color': color,
            'document_state': doc.get_state()
        }
    
    def leave_document(self, doc_id: str, user_id: str, websocket):
        """Usuario sale de un documento"""
        doc = self.documents.get(doc_id)
        if doc:
            doc.remove_user(user_id)
        
        # Remover conexión WebSocket
        if doc_id in self.connections:
            self.connections[doc_id].discard(websocket)
    
    def apply_change(self, doc_id: str, change_data: Dict) -> Dict:
        """Aplica cambio y retorna resultado"""
        doc = self.documents.get(doc_id)
        if not doc:
            return {'success': False, 'error': 'Documento no encontrado'}
        
        # Crear objeto de cambio
        change = DocumentChange(
            change_id=hashlib.md5(f"{doc_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            doc_id=doc_id,
            user_id=change_data['user_id'],
            change_type=change_data['change_type'],
            position=change_data.get('position', 0),
            content=change_data['content'],
            timestamp=datetime.now().isoformat()
        )
        
        # Aplicar cambio
        success = doc.apply_change(change)
        
        if success:
            return {
                'success': True,
                'change': change.to_dict(),
                'new_version': doc.version
            }
        else:
            return {'success': False, 'error': 'No se pudo aplicar el cambio'}
    
    def broadcast_change(self, doc_id: str, change: Dict, exclude_websocket=None):
        """Envía cambio a todos los usuarios conectados excepto el emisor"""
        if doc_id not in self.connections:
            return
        
        message = json.dumps({
            'type': 'change',
            'change': change
        })
        
        disconnected = []
        for ws in self.connections[doc_id]:
            if ws != exclude_websocket:
                try:
                    # En producción, esto sería: await ws.send_text(message)
                    # Por ahora simulamos
                    pass
                except Exception as e:
                    logger.error(f"Error enviando a WebSocket: {e}")
                    disconnected.append(ws)
        
        # Limpiar conexiones desconectadas
        for ws in disconnected:
            self.connections[doc_id].discard(ws)
    
    def update_cursor(self, doc_id: str, user_id: str, position: int) -> Dict:
        """Actualiza posición del cursor"""
        doc = self.documents.get(doc_id)
        if not doc:
            return {'success': False}
        
        doc.update_cursor(user_id, position)
        
        return {
            'success': True,
            'user_id': user_id,
            'position': position
        }
    
    def get_document_state(self, doc_id: str) -> Optional[Dict]:
        """Obtiene estado actual del documento"""
        doc = self.documents.get(doc_id)
        return doc.get_state() if doc else None
    
    def get_change_history(self, doc_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene historial de cambios"""
        doc = self.documents.get(doc_id)
        if not doc:
            return []
        
        history = doc.change_history[-limit:]
        return [change.to_dict() for change in history]
    
    def save_snapshot(self, doc_id: str) -> Dict:
        """Guarda snapshot del documento"""
        doc = self.documents.get(doc_id)
        if not doc:
            return {'success': False}
        
        snapshot = {
            'doc_id': doc_id,
            'content': doc.content,
            'version': doc.version,
            'timestamp': datetime.now().isoformat(),
            'change_count': len(doc.change_history)
        }
        
        logger.info(f"✓ Snapshot guardado para documento {doc_id} (versión {doc.version})")
        
        return {
            'success': True,
            'snapshot': snapshot
        }
    
    def get_active_documents(self) -> List[Dict]:
        """Lista documentos activos con usuarios"""
        active = []
        for doc_id, doc in self.documents.items():
            if doc.active_users:
                active.append({
                    'doc_id': doc_id,
                    'user_count': len(doc.active_users),
                    'users': [u.username for u in doc.active_users.values()],
                    'version': doc.version
                })
        return active


# Instancia global
collaborative_editor = CollaborativeEditorService()
