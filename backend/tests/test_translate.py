"""
Testes dos endpoints de traducao
"""
from types import SimpleNamespace

import pytest

from app.api.routes import translate as translate_route


@pytest.fixture
def mock_translate_dependencies(monkeypatch):
    """Mocka configuracao e servicos externos para testes offline."""
    settings = SimpleNamespace(anthropic_api_key="test-key")
    monkeypatch.setattr(translate_route, "get_settings", lambda: settings)
    return settings


def test_translate_text_endpoint_exists(client, sample_medical_text, mock_translate_dependencies, monkeypatch):
    """Testa se o endpoint de traducao de texto existe e aceita requisicoes."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "laudo", "message": "Documento medico"}

    class FakeTranslator:
        def translate_text(self, text, tipo, categoria):
            return {
                "resumo": "Resumo",
                "detalhado": "Detalhado",
                "entenda_facil": "Facil",
                "glossario": {},
                "alertas": [],
                "is_saude_mental": False,
            }

    monkeypatch.setattr(translate_route, "DocumentValidator", FakeValidator)
    monkeypatch.setattr(translate_route, "MedicalTranslator", FakeTranslator)

    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "laudo",
            "document_type": "exame_sangue",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_translate_text_returns_expected_structure(client, sample_medical_text, mock_translate_dependencies, monkeypatch):
    """Testa se a resposta tem a estrutura esperada."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "laudo", "message": "Documento medico"}

    class FakeTranslator:
        def translate_text(self, text, tipo, categoria):
            return {
                "resumo": "Resumo",
                "detalhado": "Detalhado",
                "entenda_facil": "Facil",
                "glossario": {"Hemacias": "Celulas vermelhas"},
                "alertas": ["Nenhum"],
                "is_saude_mental": False,
            }

    monkeypatch.setattr(translate_route, "DocumentValidator", FakeValidator)
    monkeypatch.setattr(translate_route, "MedicalTranslator", FakeTranslator)

    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "laudo",
            "document_type": "exame_sangue",
        }
    )
    data = response.json()
    result = data["data"]

    assert "resumo" in result
    assert "detalhado" in result
    assert "entenda_facil" in result
    assert "glossario" in result
    assert "alertas" in result
    assert "is_saude_mental" in result


def test_translate_text_validates_minimum_length(client):
    """Testa validacao de texto muito curto."""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": "curto",
            "category": "laudo",
            "document_type": "exame_sangue",
        }
    )
    assert response.status_code == 422


def test_translate_text_validates_category(client, sample_medical_text):
    """Testa validacao de categoria invalida."""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "invalid_category",
            "document_type": "exame_sangue",
        }
    )
    assert response.status_code == 422


def test_translate_text_saude_mental_flag(client, sample_medical_text, mock_translate_dependencies, monkeypatch):
    """Testa se is_saude_mental e True para categoria saude_mental."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "saude_mental", "message": "Documento de saude mental"}

    class FakeTranslator:
        def translate_text(self, text, tipo, categoria):
            return {
                "resumo": "Resumo",
                "detalhado": "Detalhado",
                "entenda_facil": "Facil",
                "glossario": {},
                "alertas": [],
                "is_saude_mental": True,
            }

    monkeypatch.setattr(translate_route, "DocumentValidator", FakeValidator)
    monkeypatch.setattr(translate_route, "MedicalTranslator", FakeTranslator)

    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "saude_mental",
            "document_type": "antidepressivo",
        }
    )
    data = response.json()
    assert data["data"]["is_saude_mental"] is True


def test_translate_file_endpoint_exists(client, mock_translate_dependencies, monkeypatch):
    """Testa se o endpoint de traducao de arquivo existe."""
    class FakeValidator:
        def validate_text(self, text):
            return {"is_valid": True, "document_type": "laudo", "message": "Documento medico"}

    class FakeTranslator:
        def translate_text(self, text, tipo, categoria):
            return {
                "resumo": "Resumo",
                "detalhado": "Detalhado",
                "entenda_facil": "Facil",
                "glossario": {},
                "alertas": [],
                "is_saude_mental": False,
            }

    async def fake_process_uploaded_file(file):
        return {
            "type": "text",
            "content": "Hemograma completo: valores normais",
            "error": None,
        }

    monkeypatch.setattr(translate_route, "DocumentValidator", FakeValidator)
    monkeypatch.setattr(translate_route, "MedicalTranslator", FakeTranslator)
    monkeypatch.setattr(translate_route, "process_uploaded_file", fake_process_uploaded_file)

    files = {"file": ("test.txt", b"Hemograma completo: valores normais", "text/plain")}
    data = {"category": "laudo", "document_type": "exame_sangue"}

    response = client.post("/api/v1/translate/file", files=files, data=data)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_translate_text_rejects_non_medical_document(
    client,
    sample_non_medical_text,
    mock_translate_dependencies,
    monkeypatch,
):
    """Garante que a API de traducao bloqueia documentos fora do escopo."""
    class FakeValidator:
        def validate_text(self, text):
            return {
                "is_valid": False,
                "document_type": None,
                "message": "O documento parece ser uma conta ou fatura, nao um documento medico.",
            }

    class FailingTranslator:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Tradutor nao deveria ser chamado para documento invalido")

    monkeypatch.setattr(translate_route, "DocumentValidator", FakeValidator)
    monkeypatch.setattr(translate_route, "MedicalTranslator", FailingTranslator)

    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_non_medical_text,
            "category": "laudo",
            "document_type": "exame_sangue",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Documento nao aceito" in data["error"]
