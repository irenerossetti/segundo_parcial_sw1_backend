"""
Tests para health check endpoint
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from main import app

client = TestClient(app)


def test_health_check():
    """Test: GET /api/health retorna status ok"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["version"] == "2.0.0"
    print("✓ Health check test passed")


def test_health_check_detailed():
    """Test: GET /api/health/detailed retorna información detallada"""
    response = client.get("/api/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "components" in data
    assert data["components"]["api"] == "ok"
    print("✓ Detailed health check test passed")


def test_root_endpoint():
    """Test: GET / retorna información del servicio"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Workflow IA/ML Service"
    assert data["status"] == "running"
    print("✓ Root endpoint test passed")


if __name__ == "__main__":
    test_health_check()
    test_health_check_detailed()
    test_root_endpoint()
    print("\n✅ All tests passed!")
