"""
Router para Gestión de Documentos integrados con Trámites
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from services.document_manager import document_manager

router = APIRouter(prefix="/api/documents", tags=["Documents"])


# Modelos Pydantic
class DocumentUploadResponse(BaseModel):
    success: bool
    document: dict
    s3_url: str
    message: str


class PermissionCheck(BaseModel):
    doc_id: str
    usuario_id: str
    role: str
    action: str


# ============= ENDPOINTS =============

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    tramite_id: str = Form(...),
    paso_workflow: str = Form(...),
    usuario_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Sube un documento asociado a un paso del trámite
    
    **Ejemplo:**
    ```
    POST /api/documents/upload
    Form Data:
    - tramite_id: "TRM-001"
    - paso_workflow: "Validación Inicial"
    - usuario_id: "user-123"
    - file: identificacion.pdf
    ```
    """
    try:
        # Leer contenido del archivo
        content = await file.read()
        
        # Subir documento
        result = document_manager.upload_document(
            tramite_id=tramite_id,
            paso_workflow=paso_workflow,
            nombre=file.filename,
            tipo=file.content_type,
            content=content,
            usuario_id=usuario_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir documento: {str(e)}")


@router.get("/tramite/{tramite_id}")
async def get_tramite_documents(tramite_id: str):
    """
    Obtiene todos los documentos de un trámite
    """
    try:
        documents = document_manager.get_tramite_documents(tramite_id)
        
        return {
            'success': True,
            'tramite_id': tramite_id,
            'documents': documents,
            'total': len(documents)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/tramite/{tramite_id}/paso/{paso_workflow}")
async def get_documents_by_paso(tramite_id: str, paso_workflow: str):
    """
    Obtiene documentos de un paso específico del workflow
    
    **Ejemplo:**
    ```
    GET /api/documents/tramite/TRM-001/paso/Validación%20Inicial
    ```
    """
    try:
        documents = document_manager.get_documents_by_paso(tramite_id, paso_workflow)
        
        return {
            'success': True,
            'tramite_id': tramite_id,
            'paso_workflow': paso_workflow,
            'documents': documents,
            'total': len(documents)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.put("/update/{doc_id}")
async def update_document(
    doc_id: str,
    usuario_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Actualiza un documento (crea nueva versión)
    """
    try:
        content = await file.read()
        
        result = document_manager.update_document(
            doc_id=doc_id,
            content=content,
            usuario_id=usuario_id
        )
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/versions/{doc_id}")
async def get_document_versions(doc_id: str):
    """
    Obtiene historial de versiones de un documento
    """
    try:
        versions = document_manager.get_document_versions(doc_id)
        
        return {
            'success': True,
            'doc_id': doc_id,
            'versions': versions,
            'total_versions': len(versions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/check-permissions")
async def check_permissions(check: PermissionCheck):
    """
    Verifica permisos de un usuario sobre un documento
    
    **Ejemplo:**
    ```json
    {
        "doc_id": "doc_TRM-001_Validación_0",
        "usuario_id": "user-123",
        "role": "cliente",
        "action": "write"
    }
    ```
    """
    try:
        has_permission = document_manager.validate_permissions(
            doc_id=check.doc_id,
            usuario_id=check.usuario_id,
            role=check.role,
            action=check.action
        )
        
        return {
            'success': True,
            'has_permission': has_permission,
            'doc_id': check.doc_id,
            'action': check.action
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/requirements/{paso_workflow}")
async def get_required_documents(paso_workflow: str):
    """
    Obtiene documentos requeridos para un paso del workflow
    
    **Ejemplo:**
    ```
    GET /api/documents/requirements/Validación%20Inicial
    ```
    """
    try:
        requirements = document_manager.get_required_documents(paso_workflow)
        
        return {
            'success': True,
            'paso_workflow': paso_workflow,
            'requirements': requirements,
            'total': len(requirements)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/check-completion/{tramite_id}/{paso_workflow}")
async def check_paso_completion(tramite_id: str, paso_workflow: str):
    """
    Verifica si un paso tiene todos los documentos requeridos
    
    **Ejemplo:**
    ```
    GET /api/documents/check-completion/TRM-001/Validación%20Inicial
    ```
    
    **Respuesta:**
    ```json
    {
        "paso": "Validación Inicial",
        "complete": true,
        "required_count": 2,
        "uploaded_count": 2,
        "missing_documents": [],
        "completion_percentage": 100
    }
    ```
    """
    try:
        result = document_manager.check_paso_completion(tramite_id, paso_workflow)
        
        return {
            'success': True,
            **result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    usuario_id: str,
    role: str
):
    """
    Elimina un documento (solo con permisos)
    
    **Query params:**
    - usuario_id: ID del usuario
    - role: Rol del usuario (admin, funcionario, cliente)
    """
    try:
        result = document_manager.delete_document(
            doc_id=doc_id,
            usuario_id=usuario_id,
            role=role
        )
        
        if not result['success']:
            raise HTTPException(status_code=403, detail=result['message'])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
