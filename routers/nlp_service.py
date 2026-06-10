"""
Router para NLP Service - Extracción de Requisitos
Endpoint: POST /api/nlp/extract-requirements
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TextInput(BaseModel):
    """Texto a procesar"""
    text: str
    language: str = "es"  # es, en
    extractEntities: bool = True


class ExtractedEntity(BaseModel):
    """Entidad extraída del texto"""
    text: str
    label: str  # PERSON, ORG, LOCATION, DATE, REQUIREMENT, etc
    confidence: float
    startChar: int
    endChar: int


class ExtractedRequirement(BaseModel):
    """Requisito extraído del texto"""
    requirement: str
    category: str  # DOCUMENTATION, PAYMENT, APPROVAL, TIMELINE, etc
    priority: str  # HIGH, MEDIUM, LOW
    confidence: float


class NLPResponse(BaseModel):
    """Respuesta del servicio NLP"""
    originalText: str
    summary: str
    entities: List[ExtractedEntity]
    requirements: List[ExtractedRequirement]
    keywords: List[str]
    sentiment: str  # POSITIVE, NEUTRAL, NEGATIVE
    language: str
    timestamp: str


@router.post("/extract-requirements", response_model=NLPResponse)
async def extract_requirements(request: TextInput):
    """
    Extrae requisitos y entidades del texto
    
    Args:
        request: Texto a procesar
        
    Returns:
        Requisitos, entidades y resumen extraído
    """
    try:
        logger.info(f"🔍 Extrayendo requisitos del texto (lang={request.language})")
        
        from services.nlp_extractor import NLPExtractor
        
        extractor = NLPExtractor(language=request.language)
        
        # Procesar texto
        result = await extractor.extract_all(
            text=request.text,
            extract_entities=request.extractEntities
        )
        
        response = NLPResponse(
            originalText=request.text,
            summary=result["summary"],
            entities=result["entities"],
            requirements=result["requirements"],
            keywords=result["keywords"],
            sentiment=result["sentiment"],
            language=request.language,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✓ Extracción completa: {len(result['requirements'])} requisitos, {len(result['entities'])} entidades")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error extrayendo requisitos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-from-file")
async def extract_from_file(file: UploadFile = File(...)):
    """
    Extrae requisitos desde un archivo (PDF, DOCX, TXT)
    """
    try:
        logger.info(f"📄 Procesando archivo: {file.filename}")
        
        # Leer contenido
        content = await file.read()
        
        from services.nlp_extractor import NLPExtractor
        
        extractor = NLPExtractor()
        result = await extractor.extract_from_file(
            file_content=content,
            filename=file.filename
        )
        
        return {
            "filename": file.filename,
            "requirements": result["requirements"],
            "entities": result["entities"],
            "keywords": result["keywords"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-texts")
async def compare_texts(text1: str, text2: str):
    """
    Compara similitud entre dos textos
    """
    try:
        logger.info("📊 Comparando textos...")
        
        from services.nlp_extractor import NLPExtractor
        
        extractor = NLPExtractor()
        similarity = await extractor.calculate_similarity(text1, text2)
        
        return {
            "similarity": similarity,
            "isMatch": similarity > 0.75,
            "text1Length": len(text1),
            "text2Length": len(text2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error comparando textos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Lista idiomas soportados
    """
    return {
        "supported": ["es", "en", "fr", "pt"],
        "default": "es"
    }
