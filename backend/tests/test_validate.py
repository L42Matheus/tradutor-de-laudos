"""
Testes dos endpoints de validacao
"""
from types import SimpleNamespace

import pytest

from app.api.routes import validate as validate_route


@pytest.fixture
def mock_validate_dependencies(monkeypatch):
    """Mocka configuracao e validador para testes offline."""
    settings = SimpleNamespace(anthropic_api_key="test-key")
    monkeypatch.setattr(validate_route, "get_settings", lambda: settings)
    return settings


def test_validate_text_endpoint_exists(client, sample_medical_text, mock_validate_dependencies, monkeypatch):
    """Testa se o endpoint de validacao de texto existe."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "laudo", "message": "Documento medico"}

    monkeypatch.setattr(validate_route, "DocumentValidator", FakeValidator)

    response = client.post(
        "/api/v1/validate/text",
        json={"text": sample_medical_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_validate_text_returns_expected_structure(client, sample_medical_text, mock_validate_dependencies, monkeypatch):
    """Testa se a resposta tem a estrutura esperada."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "laudo", "message": "Documento medico"}

    monkeypatch.setattr(validate_route, "DocumentValidator", FakeValidator)

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
    """Testa validacao de texto muito curto."""
    response = client.post(
        "/api/v1/validate/text",
        json={"text": "curto"}
    )
    assert response.status_code == 422


def test_validate_file_endpoint_exists(client, mock_validate_dependencies, monkeypatch):
    """Testa se o endpoint de validacao de arquivo existe."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "laudo", "message": "Documento medico"}

    async def fake_process_uploaded_file(file):
        return {
            "type": "text",
            "content": "Hemograma completo: valores normais",
            "error": None,
        }

    monkeypatch.setattr(validate_route, "DocumentValidator", FakeValidator)
    monkeypatch.setattr(validate_route, "process_uploaded_file", fake_process_uploaded_file)

    files = {"file": ("test.txt", b"Hemograma completo: valores normais", "text/plain")}
    response = client.post("/api/v1/validate/file", files=files)
    assert response.status_code == 200


def test_validate_text_rejects_non_medical_document(
    client,
    sample_non_medical_text,
    mock_validate_dependencies,
    monkeypatch,
):
    """Garante que o endpoint de validacao segue recusando documentos fora do escopo."""
    class FakeValidator:
        def validate_text(self, text):
            return {
                "is_valid": False,
                "document_type": None,
                "message": "O documento parece ser uma conta ou fatura, nao um documento medico.",
            }

    monkeypatch.setattr(validate_route, "DocumentValidator", FakeValidator)

    response = client.post(
        "/api/v1/validate/text",
        json={"text": sample_non_medical_text}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["is_valid"] is False
