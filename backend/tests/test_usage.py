"""
Testes dos endpoints de controle de uso
"""
import pytest


def test_usage_status_creates_new_session(client):
    """Testa se uma nova sessão é criada quando não existe"""
    response = client.get("/api/v1/usage/status")
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["translations_used"] == 0
    assert data["data"]["translations_remaining"] == 3
    assert data["data"]["is_limit_reached"] is False


def test_usage_status_with_existing_session(client):
    """Testa se a sessão existente é reconhecida"""
    session_id = "test-session-123"

    response = client.get(
        "/api/v1/usage/status",
        headers={"X-Session-ID": session_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["session_id"] == session_id


def test_usage_increment(client):
    """Testa incremento do contador de uso"""
    session_id = "test-increment-session"

    # Primeira chamada - cria sessão com 0 traduções
    client.get("/api/v1/usage/status", headers={"X-Session-ID": session_id})

    # Incrementa
    response = client.post(
        "/api/v1/usage/increment",
        headers={"X-Session-ID": session_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["translations_used"] == 1
    assert data["data"]["translations_remaining"] == 2


def test_usage_limit_reached(client):
    """Testa se o limite é detectado corretamente"""
    session_id = "test-limit-session"

    # Incrementa 3 vezes (limite padrão)
    for _ in range(3):
        client.post("/api/v1/usage/increment", headers={"X-Session-ID": session_id})

    # Verifica status
    response = client.get(
        "/api/v1/usage/status",
        headers={"X-Session-ID": session_id}
    )
    data = response.json()
    assert data["data"]["is_limit_reached"] is True
    assert data["data"]["translations_remaining"] == 0


def test_usage_reset(client):
    """Testa reset do contador de uso"""
    session_id = "test-reset-session"

    # Incrementa algumas vezes
    client.post("/api/v1/usage/increment", headers={"X-Session-ID": session_id})
    client.post("/api/v1/usage/increment", headers={"X-Session-ID": session_id})

    # Reseta
    response = client.post(
        "/api/v1/usage/reset",
        headers={"X-Session-ID": session_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["translations_used"] == 0
    assert data["data"]["translations_remaining"] == 3
