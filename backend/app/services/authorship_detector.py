"""
Servico para deteccao explicita de indicios de autoria profissional.

A deteccao e informativa: ajuda a contextualizar a formalidade do documento,
mas nao autentica juridicamente a sua origem.
"""

import json
import re
from typing import Any

import anthropic

from app.config import get_settings
from app.services.cache import CacheKeyGenerator, get_cache


IMAGE_DETECTION_PROMPT = """
Analise a imagem enviada e responda APENAS com JSON sobre indicios de autoria profissional.

Considere como indicios validos:
- numero de registro profissional medico, como CRM ou CRM/UF
- carimbo medico
- assinatura manuscrita ou assinatura digital acompanhada de identificacao profissional
- termos como Dr., Dra., Medico(a), Responsavel tecnico
- cabecalho ou rodape tipico de emissao formal de documento clinico

Regras:
- Seja conservador. Se houver duvida, use false.
- Nao valide autenticidade legal do documento.
- Detecte apenas indicios observaveis na imagem.
- Limite as evidencias a frases curtas e concretas.

Responda no formato:
{
  "professional_authorship_detected": true ou false,
  "professional_authorship_evidence": ["evidencia 1", "evidencia 2"]
}
"""


class ProfessionalAuthorshipDetector:
    """Detecta indicios de autoria profissional em texto ou imagem."""

    _PATTERN_LABELS: tuple[tuple[str, re.Pattern[str]], ...] = (
        (
            "numero de registro profissional",
            re.compile(r"\bCRM(?:[-/ ]?[A-Z]{2})?[: ]?\s?\d{3,8}\b", re.IGNORECASE),
        ),
        (
            "referencia a carimbo medico",
            re.compile(r"\bcarimbo(?:\s+medico)?\b", re.IGNORECASE),
        ),
        (
            "referencia a assinatura",
            re.compile(r"\bassinatura(?:\s+(?:medica|digital))?\b", re.IGNORECASE),
        ),
        (
            "titulo profissional medico",
            re.compile(r"\b(?:dr\.?|dra\.?|medico(?:a)?|responsavel tecnico)\b", re.IGNORECASE),
        ),
        (
            "especialidade medica informada",
            re.compile(r"\b(?:radiologista|psiquiatra|ortopedista|cardiologista|clinico geral)\b", re.IGNORECASE),
        ),
    )

    _EMISSION_MARKERS: tuple[str, ...] = (
        "hospital",
        "clinica",
        "laboratorio",
        "pronto atendimento",
        "receituario",
        "resultado assinado",
    )

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key
        self.model = settings.claude_model
        self.max_tokens = 300
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.use_cache = settings.cache_enabled
        self._cache = get_cache() if self.use_cache else None

    def detect_from_text(self, text: str) -> dict[str, Any]:
        """Detecta indicios de autoria profissional em texto usando heuristicas auditaveis."""
        cache_key = None
        if self.use_cache and self._cache:
            cache_key = CacheKeyGenerator.generate(
                content=text or "",
                tipo="authorship",
                categoria="text",
                namespace="authorship",
            )
            cached_result = self._cache.get(cache_key)
            if cached_result:
                return cached_result

        evidences: list[str] = []
        source_text = text or ""

        for label, pattern in self._PATTERN_LABELS:
            if pattern.search(source_text):
                evidences.append(label)

        normalized = source_text.lower()
        emission_hits = [marker for marker in self._EMISSION_MARKERS if marker in normalized]
        if len(emission_hits) >= 2:
            evidences.append("estrutura textual compativel com emissao clinica formal")

        evidences = self._dedupe(evidences)
        result = {
            "professional_authorship_detected": bool(evidences),
            "professional_authorship_evidence": evidences,
        }
        if self.use_cache and self._cache and cache_key:
            self._cache.set(cache_key, result)
        return result

    def detect_from_image(self, image_base64: str, media_type: str) -> dict[str, Any]:
        """Detecta indicios de autoria profissional em imagem com apoio multimodal."""
        cache_key = None
        if self.use_cache and self._cache:
            cache_key = CacheKeyGenerator.generate_from_image(
                image_base64=image_base64,
                tipo="authorship",
                categoria=media_type,
                namespace="authorship",
            )
            cached_result = self._cache.get(cache_key)
            if cached_result:
                return cached_result

        if not self.client:
            return self._empty_result()

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": IMAGE_DETECTION_PROMPT,
                            },
                        ],
                    }
                ],
            )
            result = self._parse_model_response(response.content[0].text)
            if self.use_cache and self._cache and cache_key:
                self._cache.set(cache_key, result)
            return result
        except Exception:
            return self._empty_result()

    def _parse_model_response(self, response_text: str) -> dict[str, Any]:
        """Faz parse robusto da resposta JSON do modelo."""
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()

            result = json.loads(json_text)
            evidences = result.get("professional_authorship_evidence", [])
            if isinstance(evidences, str):
                evidences = [evidences] if evidences else []
            if not isinstance(evidences, list):
                evidences = []

            cleaned = self._dedupe([str(item).strip() for item in evidences if str(item).strip()])
            detected = bool(result.get("professional_authorship_detected", False) or cleaned)

            return {
                "professional_authorship_detected": detected,
                "professional_authorship_evidence": cleaned,
            }
        except json.JSONDecodeError:
            return self._empty_result()

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            normalized = item.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(item)
        return ordered

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        return {
            "professional_authorship_detected": False,
            "professional_authorship_evidence": [],
        }
