"""
Testes dos endpoints de tradução
"""
import pytest


def test_translate_text_endpoint_exists(client, sample_medical_text):
    """Testa se o endpoint de tradução de texto existe e aceita requisições"""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "laudo",
            "document_type": "exame_sangue"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_translate_text_returns_expected_structure(client, sample_medical_text):
    """Testa se a resposta tem a estrutura esperada"""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "laudo",
            "document_type": "exame_sangue"
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
    """Testa validação de texto muito curto"""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": "curto",
            "category": "laudo",
            "document_type": "exame_sangue"
        }
    )
    assert response.status_code == 422  # Validation error


def test_translate_text_validates_category(client, sample_medical_text):
    """Testa validação de categoria inválida"""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "invalid_category",
            "document_type": "exame_sangue"
        }
    )
    assert response.status_code == 422


def test_translate_text_saude_mental_flag(client, sample_medical_text):
    """Testa se is_saude_mental é True para categoria saude_mental"""
    response = client.post(
        "/api/v1/translate/text",
        json={
            "text": sample_medical_text,
            "category": "saude_mental",
            "document_type": "antidepressivo"
        }
    )
    data = response.json()
    assert data["data"]["is_saude_mental"] is True


def test_translate_file_endpoint_exists(client):
    """Testa se o endpoint de tradução de arquivo existe"""
    # Cria um arquivo de teste simples
    files = {"file": ("test.txt", b"Hemograma completo: valores normais", "text/plain")}
    data = {"category": "laudo", "document_type": "exame_sangue"}

    response = client.post("/api/v1/translate/file", files=files, data=data)
    assert response.status_code == 200
