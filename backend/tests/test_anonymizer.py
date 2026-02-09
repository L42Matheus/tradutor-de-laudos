"""
Testes do serviço de anonimização
"""
import pytest
from app.services.anonymizer import anonymize_text


def test_anonymize_cpf():
    """Testa remoção de CPF"""
    text = "Paciente com CPF 123.456.789-00 foi atendido"
    result, removed = anonymize_text(text)

    assert "123.456.789-00" not in result
    assert "[CPF REMOVIDO]" in result
    assert "CPF" in removed


def test_anonymize_cpf_without_dots():
    """Testa remoção de CPF sem formatação"""
    text = "CPF: 12345678900"
    result, removed = anonymize_text(text)

    assert "12345678900" not in result
    assert "CPF" in removed


def test_anonymize_phone():
    """Testa remoção de telefone"""
    text = "Contato: (11) 98765-4321"
    result, removed = anonymize_text(text)

    assert "98765-4321" not in result
    assert "Telefone" in removed


def test_anonymize_email():
    """Testa remoção de email"""
    text = "Email: paciente@email.com"
    result, removed = anonymize_text(text)

    assert "paciente@email.com" not in result
    assert "Email" in removed


def test_anonymize_birth_date():
    """Testa remoção de data de nascimento"""
    text = "Data de nascimento: 15/03/1985"
    result, removed = anonymize_text(text)

    assert "15/03/1985" not in result
    assert "Data de Nascimento" in removed


def test_anonymize_name():
    """Testa remoção de nome"""
    text = "Paciente: João Silva Santos"
    result, removed = anonymize_text(text)

    assert "João Silva Santos" not in result
    assert "[NOME REMOVIDO]" in result
    assert "Nome" in removed


def test_anonymize_cns():
    """Testa remoção de CNS/Cartão SUS"""
    text = "CNS: 123 4567 8901 2345"
    result, removed = anonymize_text(text)

    assert "123 4567 8901 2345" not in result
    assert "CNS/Cartao SUS" in removed


def test_anonymize_multiple_fields():
    """Testa remoção de múltiplos campos"""
    text = """
    Paciente: Maria José
    CPF: 111.222.333-44
    Telefone: (11) 99999-8888
    Email: maria@email.com
    Data de nascimento: 20/05/1990
    """
    result, removed = anonymize_text(text)

    assert len(removed) >= 4
    assert "[CPF REMOVIDO]" in result
    assert "[TELEFONE REMOVIDO]" in result
    assert "[EMAIL REMOVIDO]" in result


def test_anonymize_preserves_medical_content():
    """Testa que conteúdo médico é preservado"""
    text = """
    Hemograma completo:
    Hemácias: 4.5 milhões/mm³
    Hemoglobina: 14.0 g/dL
    Leucócitos: 7.500/mm³
    """
    result, removed = anonymize_text(text)

    assert "Hemograma completo" in result
    assert "4.5 milhões/mm³" in result
    assert "14.0 g/dL" in result
    assert len(removed) == 0


def test_anonymize_returns_empty_list_when_no_data():
    """Testa que retorna lista vazia quando não há dados para remover"""
    text = "Exame de sangue com resultados normais"
    result, removed = anonymize_text(text)

    assert result == text
    assert len(removed) == 0
