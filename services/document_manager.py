"""
Gestor de Documentos integrado con Trámites
Permite subir, versionar y colaborar en documentos
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class DocumentMetadata:
    """Metadatos de un documento"""
    def __init__(self, 
                 id: str,
                 tramite_id: str,
                 nombre: str,
                 tipo: str,
                 paso_workflow: str,
                 version: int = 1,
                 size: int = 0,
                 hash_md5: str = "",
                 subido_por: str = "",
                 fecha_subida: str = "",
                 permisos: List[Dict] = None):
        self.id = id
        self.tramite_id = tramite_id
        self.nombre = nombre
        self.tipo = tipo
        self.paso_workflow = paso_workflow
        self.version = version
        self.size = size
        self.hash_md5 = hash_md5
        self.subido_por = subido_por
        self.fecha_subida = fecha_subida or datetime.now().isoformat()
        self.permisos = permisos or []
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'tramite_id': self.tramite_id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'paso_workflow': self.paso_workflow,
            'version': self.version,
            'size': self.size,
            'hash_md5': self.hash_md5,
            'subido_por': self.subido_por,
            'fecha_subida': self.fecha_subida,
            'permisos': self.permisos
        }


class DocumentManager:
    """
    Gestor de documentos con integración a trámites
    """
    
    def __init__(self):
        # Simulación de almacenamiento en memoria
        # En producción, esto estaría en MongoDB + S3
        self.documents: Dict[str, DocumentMetadata] = {}
        self.document_versions: Dict[str, List[DocumentMetadata]] = {}
        self.tramite_documents: Dict[str, List[str]] = {}
    
    def upload_document(self,
                       tramite_id: str,
                       paso_workflow: str,
                       nombre: str,
                       tipo: str,
                       content: bytes,
                       usuario_id: str) -> Dict[str, Any]:
        """
        Sube un documento asociado a un paso del trámite
        
        Args:
            tramite_id: ID del trámite
            paso_workflow: Nombre del paso actual del workflow
            nombre: Nombre del archivo
            tipo: MIME type
            content: Contenido del archivo en bytes
            usuario_id: ID del usuario que sube
        
        Returns:
            Metadatos del documento subido
        """
        # Generar ID único
        doc_id = f"doc_{tramite_id}_{paso_workflow}_{len(self.documents)}"
        
        # Calcular hash MD5
        hash_md5 = hashlib.md5(content).hexdigest()
        
        # Crear metadatos
        doc = DocumentMetadata(
            id=doc_id,
            tramite_id=tramite_id,
            nombre=nombre,
            tipo=tipo,
            paso_workflow=paso_workflow,
            version=1,
            size=len(content),
            hash_md5=hash_md5,
            subido_por=usuario_id,
            fecha_subida=datetime.now().isoformat(),
            permisos=[
                {'usuario_id': usuario_id, 'nivel': 'owner'},
                {'role': 'funcionario', 'nivel': 'write'},
                {'role': 'admin', 'nivel': 'admin'}
            ]
        )
        
        # Almacenar
        self.documents[doc_id] = doc
        
        # Asociar con trámite
        if tramite_id not in self.tramite_documents:
            self.tramite_documents[tramite_id] = []
        self.tramite_documents[tramite_id].append(doc_id)
        
        # Inicializar versiones
        self.document_versions[doc_id] = [doc]
        
        logger.info(f"✓ Documento subido: {doc_id} para trámite {tramite_id}, paso {paso_workflow}")
        
        return {
            'success': True,
            'document': doc.to_dict(),
            's3_url': f"s3://workflow-docs/{tramite_id}/{paso_workflow}/{nombre}",
            'message': 'Documento subido exitosamente'
        }
    
    def get_tramite_documents(self, tramite_id: str) -> List[Dict]:
        """
        Obtiene todos los documentos de un trámite
        """
        doc_ids = self.tramite_documents.get(tramite_id, [])
        
        documents = []
        for doc_id in doc_ids:
            if doc_id in self.documents:
                documents.append(self.documents[doc_id].to_dict())
        
        return documents
    
    def get_documents_by_paso(self, tramite_id: str, paso_workflow: str) -> List[Dict]:
        """
        Obtiene documentos de un paso específico del workflow
        """
        doc_ids = self.tramite_documents.get(tramite_id, [])
        
        documents = []
        for doc_id in doc_ids:
            doc = self.documents.get(doc_id)
            if doc and doc.paso_workflow == paso_workflow:
                documents.append(doc.to_dict())
        
        return documents
    
    def update_document(self, 
                       doc_id: str,
                       content: bytes,
                       usuario_id: str) -> Dict[str, Any]:
        """
        Actualiza un documento (crea nueva versión)
        """
        if doc_id not in self.documents:
            return {'success': False, 'message': 'Documento no encontrado'}
        
        old_doc = self.documents[doc_id]
        
        # Crear nueva versión
        new_version = old_doc.version + 1
        hash_md5 = hashlib.md5(content).hexdigest()
        
        new_doc = DocumentMetadata(
            id=doc_id,
            tramite_id=old_doc.tramite_id,
            nombre=old_doc.nombre,
            tipo=old_doc.tipo,
            paso_workflow=old_doc.paso_workflow,
            version=new_version,
            size=len(content),
            hash_md5=hash_md5,
            subido_por=usuario_id,
            fecha_subida=datetime.now().isoformat(),
            permisos=old_doc.permisos
        )
        
        # Actualizar documento actual
        self.documents[doc_id] = new_doc
        
        # Guardar en historial de versiones
        self.document_versions[doc_id].append(new_doc)
        
        logger.info(f"✓ Documento actualizado: {doc_id} → versión {new_version}")
        
        return {
            'success': True,
            'document': new_doc.to_dict(),
            'previous_version': old_doc.version,
            'message': f'Documento actualizado a versión {new_version}'
        }
    
    def get_document_versions(self, doc_id: str) -> List[Dict]:
        """
        Obtiene historial de versiones de un documento
        """
        if doc_id not in self.document_versions:
            return []
        
        return [doc.to_dict() for doc in self.document_versions[doc_id]]
    
    def validate_permissions(self, 
                           doc_id: str,
                           usuario_id: str,
                           role: str,
                           action: str) -> bool:
        """
        Valida si un usuario tiene permisos para realizar una acción
        
        Args:
            doc_id: ID del documento
            usuario_id: ID del usuario
            role: Rol del usuario (admin, funcionario, cliente)
            action: Acción (read, write, delete, admin)
        
        Returns:
            True si tiene permiso, False si no
        """
        if doc_id not in self.documents:
            return False
        
        doc = self.documents[doc_id]
        
        # Admin siempre tiene acceso
        if role == 'admin':
            return True
        
        # Verificar permisos específicos
        for permiso in doc.permisos:
            if permiso.get('usuario_id') == usuario_id:
                nivel = permiso.get('nivel')
                if nivel == 'owner' or nivel == 'admin':
                    return True
                if action == 'read' and nivel in ['read', 'write', 'owner']:
                    return True
                if action == 'write' and nivel in ['write', 'owner']:
                    return True
            
            # Permisos por rol
            if permiso.get('role') == role:
                nivel = permiso.get('nivel')
                if nivel == 'admin':
                    return True
                if action == 'read' and nivel in ['read', 'write']:
                    return True
                if action == 'write' and nivel == 'write':
                    return True
        
        return False
    
    def get_required_documents(self, paso_workflow: str) -> List[Dict]:
        """
        Retorna documentos requeridos para un paso del workflow
        """
        # Configuración de documentos requeridos por paso
        requirements = {
            'Validación Inicial': [
                {'nombre': 'Identificación oficial', 'tipo': 'PDF', 'obligatorio': True},
                {'nombre': 'Comprobante de domicilio', 'tipo': 'PDF', 'obligatorio': True}
            ],
            'Análisis Técnico': [
                {'nombre': 'Documentación técnica', 'tipo': 'PDF', 'obligatorio': True},
                {'nombre': 'Planos o diagramas', 'tipo': 'PDF/DWG', 'obligatorio': False}
            ],
            'Análisis Legal': [
                {'nombre': 'Contrato', 'tipo': 'PDF/DOCX', 'obligatorio': True},
                {'nombre': 'Documentos legales', 'tipo': 'PDF', 'obligatorio': True}
            ],
            'Aprobación Final': [
                {'nombre': 'Resumen ejecutivo', 'tipo': 'PDF', 'obligatorio': True},
                {'nombre': 'Firmas autorizadas', 'tipo': 'PDF', 'obligatorio': True}
            ]
        }
        
        return requirements.get(paso_workflow, [])
    
    def check_paso_completion(self, tramite_id: str, paso_workflow: str) -> Dict[str, Any]:
        """
        Verifica si un paso tiene todos los documentos requeridos
        """
        required = self.get_required_documents(paso_workflow)
        uploaded = self.get_documents_by_paso(tramite_id, paso_workflow)
        
        # Verificar documentos obligatorios
        obligatorios = [req for req in required if req.get('obligatorio', False)]
        uploaded_names = [doc['nombre'] for doc in uploaded]
        
        missing = []
        for req in obligatorios:
            if req['nombre'] not in uploaded_names:
                missing.append(req['nombre'])
        
        is_complete = len(missing) == 0
        
        return {
            'paso': paso_workflow,
            'complete': is_complete,
            'required_count': len(obligatorios),
            'uploaded_count': len(uploaded),
            'missing_documents': missing,
            'completion_percentage': (len(uploaded) / len(obligatorios) * 100) if obligatorios else 100
        }
    
    def delete_document(self, doc_id: str, usuario_id: str, role: str) -> Dict[str, Any]:
        """
        Elimina un documento (solo si tiene permisos)
        """
        if not self.validate_permissions(doc_id, usuario_id, role, 'delete'):
            return {
                'success': False,
                'message': 'No tienes permisos para eliminar este documento'
            }
        
        if doc_id not in self.documents:
            return {'success': False, 'message': 'Documento no encontrado'}
        
        doc = self.documents[doc_id]
        tramite_id = doc.tramite_id
        
        # Eliminar de almacenamiento
        del self.documents[doc_id]
        
        # Eliminar de trámite
        if tramite_id in self.tramite_documents:
            self.tramite_documents[tramite_id].remove(doc_id)
        
        # Eliminar versiones
        if doc_id in self.document_versions:
            del self.document_versions[doc_id]
        
        logger.info(f"✓ Documento eliminado: {doc_id}")
        
        return {
            'success': True,
            'message': 'Documento eliminado exitosamente'
        }


# Instancia global
document_manager = DocumentManager()
