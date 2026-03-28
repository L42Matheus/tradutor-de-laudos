"""
Testes unitarios do validador de documentos
"""
from types import SimpleNamespace

from app.services.cache import InMemoryCache
from app.services.validator import DocumentValidator


def _build_validator() -> DocumentValidator:
    """Cria instancia sem executar __init__ para testar regras locais."""
    return DocumentValidator.__new__(DocumentValidator)


def test_validator_rejects_utility_bill_text():
    """Conta de luz deve ser recusada sem depender do modelo."""
    validator = _build_validator()
    text = """
    CONTA DE LUZ
    Unidade consumidora: 123456
    Consumo: 150 kWh
    Vencimento: 15/03/2026
    """

    reason = validator._get_text_rejection_reason(text)

    assert reason is not None
    assert "conta" in reason.lower() or "fatura" in reason.lower()


def test_validator_rejects_chord_sheet_text():
    """Cifra com acordes deve ser recusada sem depender do modelo."""
    validator = _build_validator()
    text = """
    Tom: G
    Intro: G D Em C
    G D Em C
    G D C D
    """

    reason = validator._get_text_rejection_reason(text)

    assert reason is not None
    assert "cifra" in reason.lower() or "musical" in reason.lower()


def test_validator_does_not_reject_medical_exam_text():
    """Texto medico valido nao deve cair no bloqueio heuristico."""
    validator = _build_validator()
    text = """
    HEMOGRAMA COMPLETO
    Hemacias: 4.5 milhoes/mm3
    Hemoglobina: 14.0 g/dL
    Leucocitos: 7500/mm3
    """

    reason = validator._get_text_rejection_reason(text)

    assert reason is None


def test_validate_image_uses_cache_for_repeated_input(monkeypatch):
    """A mesma imagem nao deve disparar o modelo mais de uma vez."""
    cache = InMemoryCache()
    calls = {"count": 0}

    class FakeMessages:
        def create(self, **kwargs):
            calls["count"] += 1
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        text='{"is_valid": true, "document_type": "receita", "message": "Documento medico"}'
                    )
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key=None):
            self.messages = FakeMessages()

    monkeypatch.setattr(
        "app.services.validator.get_settings",
        lambda: SimpleNamespace(
            anthropic_api_key="test-key",
            claude_model="test-model",
            cache_enabled=True,
        ),
    )
    monkeypatch.setattr("app.services.validator.get_cache", lambda: cache)
    monkeypatch.setattr("app.services.validator.anthropic.Anthropic", FakeAnthropic)

    validator = DocumentValidator()
    image_data = "base64-image-content"

    result1 = validator.validate_image(image_data, "image/png")
    result2 = validator.validate_image(image_data, "image/png")

    assert result1 == result2
    assert calls["count"] == 1
