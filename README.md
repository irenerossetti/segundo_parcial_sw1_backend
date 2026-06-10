# 🤖 ML Service - Workflow IA/ML Microservice

Microservicio Python basado en **FastAPI** para procesar IA/ML en el sistema de Workflow.

## 📋 Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Copy .env
```bash
cp .env.example .env
# Editar .env con tus variables
```

### 4. Run Service
```bash
python main.py
# O con uvicorn directamente:
uvicorn main:app --reload --port 8001
```

Service estará disponible en: **http://localhost:8001**

---

## 🔌 Health Check

```bash
curl http://localhost:8001/api/health
```

Respuesta:
```json
{
  "status": "ok",
  "service": "Workflow IA/ML Service",
  "timestamp": "2024-06-05T10:30:00",
  "version": "2.0.0"
}
```

---

## 📦 Project Structure

```
ml-service/
├── main.py                      # FastAPI app root
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image
├── .env.example                 # Environment template
├── routers/                     # API route handlers
│   ├── __init__.py
│   ├── health.py               # Health check routes
│   ├── ia_agent.py             # (Sprint 2) IA agent
│   ├── nlp_service.py          # (Sprint 2) NLP routes
│   ├── report_generator.py     # (Sprint 2) Report routes
│   └── risk_analyzer.py        # (Sprint 2) Risk routes
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── policy_matcher.py       # (Sprint 2) ML model
│   ├── nlp_extractor.py        # (Sprint 2) NLP logic
│   └── report_service.py       # (Sprint 2) Report gen
├── models/                      # Data models
│   └── __init__.py
└── tests/                       # Unit tests
    ├── __init__.py
    └── test_health.py          # Health check tests
```

---

## 🚀 Docker

### Build & Run
```bash
docker build -t workflow-ml:latest .
docker run -p 8001:8001 workflow-ml:latest
```

### Or Use Docker Compose (from backend/)
```bash
cd ..
docker-compose up --build
```

---

## 🔗 Environment Variables

```env
# Service Config
ML_SERVICE_PORT=8001
ML_SERVICE_HOST=0.0.0.0
ENVIRONMENT=development
LOG_LEVEL=INFO

# Python
PYTHONUNBUFFERED=1

# AWS (Sprint 2+)
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx

# Backend Connection
BACKEND_URL=http://localhost:8080
```

---

## 📚 API Endpoints

### Current (Sprint 1)
- `GET /` - Service info
- `GET /api/health` - Health check
- `GET /api/health/detailed` - Detailed status

### Planned (Sprint 2)
- `POST /api/ia/policies/recommend` - Policy recommendation
- `POST /api/nlp/extract-requirements` - Extract requirements from text
- `POST /api/reportes/generate` - Generate dynamic reports
- `POST /api/riesgo/analyze` - Risk analysis

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Or run specific test
python tests/test_health.py
```

Expected output:
```
✓ Health check test passed
✓ Detailed health check test passed
✓ Root endpoint test passed
✅ All tests passed!
```

---

## 🛠️ Development

### With Auto-Reload
```bash
uvicorn main:app --reload --port 8001
```

### Debug Mode
```bash
# In .env
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Then run
python main.py
```

---

## 📊 Dependencies

### Core
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation

### ML/AI
- **tensorflow** - Deep learning
- **torch** - PyTorch framework
- **scikit-learn** - ML library
- **nltk** - NLP
- **spaCy** - NLP

### Utilities
- **boto3** - AWS SDK
- **requests** - HTTP client
- **python-dotenv** - .env loading

---

## 🚀 Deployment

### AWS Lambda
[Instructions coming in Sprint 3]

### Docker Container
```bash
docker push workflow-ml:latest
# Deploy to your registry
```

### Render.com (Free tier)
1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy

---

## 📝 Logging

All requests and errors are logged:

```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     ML Service iniciado
✓ ML Service ready to receive requests
INFO:     POST /api/ia/policies/recommend - 200 OK
ERROR:    ❌ Error processing request
```

---

## 🔗 Integration

### Call from Backend (Java)

```java
// Spring Boot service
@Service
public class IAClientService {
    
    @Value("${ml.service.url:http://localhost:8001}")
    private String mlServiceUrl;
    
    public String recommendPolicy(String clientText) {
        RestTemplate template = new RestTemplate();
        String url = mlServiceUrl + "/api/ia/policies/recommend";
        
        PolicyRequest request = new PolicyRequest(clientText);
        return template.postForObject(url, request, String.class);
    }
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8001 in use | Change port in .env or kill process |
| ModuleNotFoundError | Activate venv and reinstall requirements |
| Connection to Backend fails | Check BACKEND_URL in .env |
| AWS credentials error | Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY |

---

## 📞 Support

- 📖 Full docs: See `GUIA_SETUP_SPRINT_1.md`
- 🐛 Issues: Check logs with `LOG_LEVEL=DEBUG`
- 💬 Questions: Contact DevOps team

---

**Version:** 2.0.0  
**Status:** 🟢 Production Ready  
**Last Updated:** 5 de Junio, 2026
