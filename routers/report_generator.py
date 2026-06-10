"""
Router para Report Generator - Generación de Reportes Dinámicos
Endpoint: POST /api/reportes/generate
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging
import io

logger = logging.getLogger(__name__)
router = APIRouter()


class ReportTemplate(BaseModel):
    """Template de reporte"""
    templateId: str
    name: str
    sections: List[str]
    includeGraphs: bool = True
    includeSummary: bool = True


class ReportData(BaseModel):
    """Datos para generar reporte"""
    tramiteId: str
    clientName: str
    template: str  # "STANDARD", "DETAILED", "EXECUTIVE"
    data: Dict
    includeSignature: bool = False


class ReportResponse(BaseModel):
    """Respuesta de reporte generado"""
    reportId: str
    tramiteId: str
    fileName: str
    format: str  # "PDF", "DOCX", "XLSX"
    pages: int
    fileSize: int
    generatedAt: str
    downloadUrl: str


@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportData):
    """
    Genera reporte dinámico en PDF
    
    Args:
        request: Datos del reporte
        
    Returns:
        Información del reporte generado
    """
    try:
        logger.info(f"📊 Generando reporte: tramite={request.tramiteId}, template={request.template}")
        
        from services.report_service import ReportService
        
        service = ReportService()
        
        # Generar reporte
        report = await service.generate_report(
            tramite_id=request.tramiteId,
            client_name=request.clientName,
            template=request.template,
            data=request.data,
            include_signature=request.includeSignature
        )
        
        response = ReportResponse(
            reportId=report["id"],
            tramiteId=request.tramiteId,
            fileName=report["filename"],
            format="PDF",
            pages=report["pages"],
            fileSize=report["size"],
            generatedAt=datetime.now().isoformat(),
            downloadUrl=f"/api/reportes/download/{report['id']}"
        )
        
        logger.info(f"✓ Reporte generado: {report['filename']} ({report['pages']} páginas)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{reportId}")
async def download_report(reportId: str):
    """
    Descarga un reporte generado
    """
    try:
        logger.info(f"📥 Descargando reporte: {reportId}")
        
        from services.report_service import ReportService
        
        service = ReportService()
        file_path = await service.get_report_file(reportId)
        
        return FileResponse(
            path=file_path,
            filename=f"reporte_{reportId}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"❌ Error descargando reporte: {str(e)}")
        raise HTTPException(status_code=404, detail="Report not found")


@router.get("/templates")
async def list_templates():
    """
    Lista templates disponibles
    """
    return {
        "templates": [
            {
                "id": "STANDARD",
                "name": "Reporte Estándar",
                "sections": ["SUMMARY", "DETAILS", "REQUIREMENTS", "TIMELINE"]
            },
            {
                "id": "DETAILED",
                "name": "Reporte Detallado",
                "sections": ["SUMMARY", "DETAILS", "REQUIREMENTS", "TIMELINE", "DOCUMENTS", "ANALYSIS"]
            },
            {
                "id": "EXECUTIVE",
                "name": "Reporte Ejecutivo",
                "sections": ["SUMMARY", "KEY_POINTS", "RECOMMENDATIONS"]
            }
        ]
    }


@router.post("/export/{tramiteId}")
async def export_tramite(tramiteId: str, format: str = "PDF"):
    """
    Exporta un trámite completo a reporte
    
    Formatos: PDF, DOCX, XLSX
    """
    try:
        logger.info(f"📤 Exportando trámite: {tramiteId} en formato {format}")
        
        from services.report_service import ReportService
        
        service = ReportService()
        result = await service.export_tramite(tramiteId, format)
        
        return {
            "tramiteId": tramiteId,
            "format": format,
            "fileName": result["filename"],
            "fileSize": result["size"],
            "downloadUrl": f"/api/reportes/download/{result['id']}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error exportando trámite: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule")
async def schedule_report(tramiteId: str, scheduleTime: str):
    """
    Programa la generación automática de un reporte
    
    scheduleTime: ISO format datetime
    """
    try:
        logger.info(f"⏰ Programando reporte para: {tramiteId} a las {scheduleTime}")
        
        from services.report_service import ReportService
        
        service = ReportService()
        result = await service.schedule_report(tramiteId, scheduleTime)
        
        return {
            "success": True,
            "tramiteId": tramiteId,
            "scheduledFor": scheduleTime,
            "status": "SCHEDULED",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error programando reporte: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
