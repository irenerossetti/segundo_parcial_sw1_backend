"""
FastAPI Microservicio para IA/ML
Servicio separado que maneja:
- Policy recommendation (Agente inteligente)
- NLP (Extracción de requisitos)
- Report generation (Reportes dinámicos)
- Risk analysis (Análisis de riesgo)
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title="Workflow IA/ML Service",
    description="Microservicio para inteligencia artificial en sistema de workflow",
    version="2.0.0"
)

# Configurar CORS
ALLOWED_ORIGINS = [
    "http://localhost:4200",      # Angular dev
    "http://localhost:8080",      # Backend dev
    "http://localhost:3000",      # React (si aplica)
    "https://tu-dominio.com",     # Producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex="http://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROUTERS - Importar después de crear app
# =============================================================================

from routers import health


# =============================================================================
# STARTUP EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Ejecutado cuando inicia la aplicación"""
    logger.info("🚀 ML Service iniciado")
    logger.info(f"Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Puerto: {os.getenv('ML_SERVICE_PORT', 8001)}")
    
    # Aquí se cargarían modelos entrenados (más tarde en Sprint 3)
    logger.info("✓ Servicio listo para recibir requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutado cuando se cierra la aplicación"""
    logger.info("🛑 ML Service cerrado")


# =============================================================================
# RUTAS PRINCIPALES
# =============================================================================

app.include_router(health.router, prefix="/api", tags=["Health"])

# Rutas para Sprint 2 - IA Features
from routers import ia_agent, nlp_service, report_generator, risk_analyzer
app.include_router(ia_agent.router, prefix="/api/ia", tags=["IA Agent"])
app.include_router(nlp_service.router, prefix="/api/nlp", tags=["NLP"])
app.include_router(report_generator.router, prefix="/api/reportes", tags=["Reportes"])
app.include_router(risk_analyzer.router, prefix="/api/riesgo", tags=["Riesgo"])

# Rutas para Sprint 3 - Advanced Features
from routers import analytics, notifications, deep_learning
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(deep_learning.router, prefix="/api/deeplearning", tags=["Deep Learning"])

# Rutas para Segundo Parcial - Agente Inteligente
from routers import intelligent_agent
app.include_router(intelligent_agent.router, tags=["Intelligent Agent"])

# Rutas para Semana 2 - Gestión de Documentos
from routers import documents
app.include_router(documents.router, tags=["Documents"])

# Rutas para Semana 2 - Predicción de Cuellos de Botella (LSTM)
from routers import bottleneck_prediction
app.include_router(bottleneck_prediction.router, tags=["Bottleneck Prediction"])

# Rutas para Semana 2 - Reportes Dinámicos con NLP
from routers import dynamic_reports
app.include_router(dynamic_reports.router, tags=["Dynamic Reports"])

# Rutas para Semana 3 - Edición Colaborativa
from routers import collaborative_docs
app.include_router(collaborative_docs.router, tags=["Collaborative Editing"])

# Rutas para Semana 3 - Dashboard Predictivo
from routers import dashboard
app.include_router(dashboard.router, tags=["Predictive Dashboard"])

# =============================================================================
# RAÍZ
# =============================================================================

@app.get("/")
async def root():
    """Raíz del servicio"""
    return {
        "service": "Workflow IA/ML Service",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejo de excepciones HTTP"""
    logger.error(f"HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo de excepciones generales"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    PORT = int(os.getenv("ML_SERVICE_PORT", 8001))
    HOST = os.getenv("ML_SERVICE_HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )
