"""
Testes dos endpoints de apoio emocional
"""
import pytest


def test_support_quote_returns_quote(client):
    """Testa se retorna uma frase de apoio"""
    response = client.get("/api/v1/support/quote")
    assert response.status_code == 200
    data = response.json()
    assert "quote" in data
    assert len(data["quote"]) > 0


def test_support_exercises_returns_list(client):
    """Testa se retorna lista de exercícios"""
    response = client.get("/api/v1/support/exercises")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verifica estrutura do exercício
    exercise = data[0]
    assert "name" in exercise
    assert "description" in exercise
    assert "steps" in exercise


def test_support_resources_returns_list(client):
    """Testa se retorna lista de recursos"""
    response = client.get("/api/v1/support/resources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verifica estrutura do recurso
    resource = data[0]
    assert "name" in resource
    assert "description" in resource
    assert "contact" in resource


def test_support_resources_has_emergency(client):
    """Testa se existe pelo menos um recurso de emergência (CVV)"""
    response = client.get("/api/v1/support/resources")
    data = response.json()

    emergency_resources = [r for r in data if r.get("is_emergency")]
    assert len(emergency_resources) > 0


def test_support_all_returns_complete_data(client):
    """Testa se o endpoint /all retorna todos os dados"""
    response = client.get("/api/v1/support/all")
    assert response.status_code == 200
    data = response.json()

    assert "quotes" in data
    assert "exercises" in data
    assert "resources" in data
    assert len(data["quotes"]) > 0
    assert len(data["exercises"]) > 0
    assert len(data["resources"]) > 0
