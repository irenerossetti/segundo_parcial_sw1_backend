"""
Mock Backend Server (Python FastAPI)
Simula los endpoints del Backend Java Spring Boot
Permite testing del sistema completo sin necesidad de Java
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from typing import Dict, Any, List

app = FastAPI(
    title="Workflow Backend Mock",
    description="Mock backend que simula Spring Boot - Redirige a ML Service",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ML Service URL
ML_SERVICE_URL = "http://localhost:8001"

# ==================== HEALTH & INFO ====================

@app.get("/api/health")
async def health():
    """Backend health check"""
    return {
        "status": "UP",
        "service": "workflow-backend-mock",
        "timestamp": "2026-06-02T10:00:00Z",
        "ml_service": f"{ML_SERVICE_URL}/api/health"
    }

# ==================== ANALYTICS ====================

@app.get("/api/analytics/metrics")
async def analytics_metrics(metricType: str = "all"):
    """Get system metrics"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/analytics/metrics",
            params={"metric_type": metricType},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e), "status": "offline"}

@app.get("/api/analytics/dashboard")
async def analytics_dashboard(userId: str = "user-123", dashType: str = "overview"):
    """Get dashboard"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/analytics/dashboard",
            params={"user_id": userId, "type": dashType},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/analytics/kpi")
async def analytics_kpi():
    """Get KPIs"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/analytics/kpi",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/analytics/trends")
async def analytics_trends(periodDays: int = 30):
    """Get trends"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/analytics/trends",
            params={"period_days": periodDays},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/analytics/performance")
async def analytics_performance():
    """Get performance metrics"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/analytics/performance",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==================== NOTIFICATIONS ====================

@app.get("/api/notifications/user/{user_id}")
async def get_notifications(user_id: str, limit: int = 20):
    """Get user notifications"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/notifications/user/{user_id}",
            params={"limit": limit},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/notifications/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/notifications/mark-read/{notification_id}",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/notifications/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get notification preferences"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/notifications/preferences/{user_id}",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/notifications/webhooks")
async def get_webhooks():
    """Get webhooks"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/notifications/webhooks",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==================== DEEP LEARNING ====================

@app.post("/api/deeplearning/predict")
async def predict(modelId: str, data: Dict[str, Any]):
    """Make prediction"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/deeplearning/predict",
            json={"model_id": modelId, "data": data},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/deeplearning/models")
async def list_models():
    """List available models"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/deeplearning/models",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/deeplearning/models/{model_id}")
async def get_model_info(model_id: str):
    """Get model info"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/deeplearning/models/{model_id}",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/deeplearning/models/{model_id}/deploy")
async def deploy_model(model_id: str, environment: str = "production"):
    """Deploy model"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/deeplearning/models/{model_id}/deploy",
            params={"environment": environment},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/deeplearning/batch-predict")
async def batch_predict(modelId: str, data: List[Dict[str, Any]]):
    """Batch predictions"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/deeplearning/batch-predict",
            params={"model_id": modelId},
            json=data,
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/deeplearning/models/{model_id}/speed")
async def get_inference_speed(model_id: str):
    """Get inference speed metrics"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/api/deeplearning/inference-speed/{model_id}",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==================== IA / LEGACY ====================

@app.get("/api/ia/health")
async def ia_health():
    """IA service health check"""
    return {
        "status": "UP",
        "service": "ia-agent",
        "timestamp": "2026-06-02T10:00:00Z"
    }

@app.post("/api/ia/policies/recommend")
async def recommend_policies(client_text: str):
    """Recommend policies"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/ia/policies/recommend",
            json={"client_text": client_text},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔════════════════════════════════════════════════╗
    ║   WORKFLOW BACKEND MOCK (Python FastAPI)       ║
    ║   Puente entre Frontend y ML Service           ║
    ║   Listening on http://0.0.0.0:8080             ║
    ║   ML Service: http://localhost:8001            ║
    ╚════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8080)
