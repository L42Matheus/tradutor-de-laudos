"""
Testes dos endpoints de validação
"""
import pytest


def test_validate_text_endpoint_exists(client, sample_medical_text):
    """Testa se o endpoint de validação de texto existe"""
    response = client.post(
        "/api/v1/validate/text",
        json={"text": sample_medical_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_validate_text_returns_expected_structure(client, sample_medical_text):
    """Testa se a resposta tem a estrutura esperada"""
    response = client.post(
        "/api/v1/validate/text",
        json={"text": sample_medical_text}
    )
    data = response.json()
    result = data["data"]

    assert "is_valid" in result
    assert "document_type" in result
    assert "message" in result


def test_validate_text_validates_minimum_length(client):
    """Testa validação de texto muito curto"""
    response = client.post(
        "/api/v1/validate/text",
        json={"text": "curto"}
    )
    assert response.status_code == 422


def test_validate_file_endpoint_exists(client):
    """Testa se o endpoint de validação de arquivo existe"""
    files = {"file": ("test.txt", b"Hemograma completo: valores normais", "text/plain")}
    response = client.post("/api/v1/validate/file", files=files)
    assert response.status_code == 200
