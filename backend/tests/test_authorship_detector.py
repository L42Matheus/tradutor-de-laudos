"""
Testes do detector de autoria profissional.
"""
from types import SimpleNamespace

from app.services.cache import InMemoryCache
from app.services.authorship_detector import ProfessionalAuthorshipDetector


def test_detect_from_text_identifies_professional_markers(monkeypatch):
    """Texto com CRM e titulo profissional deve gerar evidencias."""
    monkeypatch.setattr(
        "app.services.authorship_detector.get_settings",
        lambda: SimpleNamespace(
            anthropic_api_key="",
            claude_model="test-model",
            cache_enabled=True,
        ),
    )
    monkeypatch.setattr("app.services.authorship_detector.get_cache", lambda: InMemoryCache())
    detector = ProfessionalAuthorshipDetector()

    result = detector.detect_from_text(
        "Hospital Municipal Pedro I. Receituario assinado. CRM-PB 12345. Dra. Arelli Pamella."
    )

    assert result["professional_authorship_detected"] is True
    assert "numero de registro profissional" in result["professional_authorship_evidence"]


def test_detect_from_text_returns_false_without_markers(monkeypatch):
    """Texto medico sem autoria profissional explicita nao deve marcar positivo."""
    monkeypatch.setattr(
        "app.services.authorship_detector.get_settings",
        lambda: SimpleNamespace(
            anthropic_api_key="",
            claude_model="test-model",
            cache_enabled=True,
        ),
    )
    monkeypatch.setattr("app.services.authorship_detector.get_cache", lambda: InMemoryCache())
    detector = ProfessionalAuthorshipDetector()

    result = detector.detect_from_text("Hemograma completo com valores dentro da normalidade.")

    assert result["professional_authorship_detected"] is False
    assert result["professional_authorship_evidence"] == []


def test_parse_model_response_for_image_detection(monkeypatch):
    """Resposta multimodal valida deve ser normalizada corretamente."""
    monkeypatch.setattr(
        "app.services.authorship_detector.get_settings",
        lambda: SimpleNamespace(
            anthropic_api_key="",
            claude_model="test-model",
            cache_enabled=True,
        ),
    )
    monkeypatch.setattr("app.services.authorship_detector.get_cache", lambda: InMemoryCache())
    detector = ProfessionalAuthorshipDetector()

    result = detector._parse_model_response(
        '{"professional_authorship_detected": true, '
        '"professional_authorship_evidence": ["carimbo medico visivel", "CRM identificado"]}'
    )

    assert result["professional_authorship_detected"] is True
    assert result["professional_authorship_evidence"] == [
        "carimbo medico visivel",
        "CRM identificado",
    ]


def test_detect_from_image_uses_cache_for_repeated_input(monkeypatch):
    """A mesma imagem nao deve disparar o modelo de autoria mais de uma vez."""
    cache = InMemoryCache()
    calls = {"count": 0}

    class FakeMessages:
        def create(self, **kwargs):
            calls["count"] += 1
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        text='{"professional_authorship_detected": true, '
                        '"professional_authorship_evidence": ["CRM identificado"]}'
                    )
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key=None):
            self.messages = FakeMessages()

    monkeypatch.setattr(
        "app.services.authorship_detector.get_settings",
        lambda: SimpleNamespace(
            anthropic_api_key="test-key",
            claude_model="test-model",
            cache_enabled=True,
        ),
    )
    monkeypatch.setattr("app.services.authorship_detector.get_cache", lambda: cache)
    monkeypatch.setattr("app.services.authorship_detector.anthropic.Anthropic", FakeAnthropic)

    detector = ProfessionalAuthorshipDetector()
    image_data = "base64-image-content"

    result1 = detector.detect_from_image(image_data, "image/png")
    result2 = detector.detect_from_image(image_data, "image/png")

    assert result1 == result2
    assert calls["count"] == 1
