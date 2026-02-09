"""
Testes do endpoint de health check
"""
import pytest


def test_health_check(client):
    """Testa se o health check retorna status healthy"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_root_endpoint(client):
    """Testa se a rota raiz retorna informações da API"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "health" in data
