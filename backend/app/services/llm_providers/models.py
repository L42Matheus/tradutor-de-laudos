"""
Catálogo de modelos disponíveis por provider.
Atualizado: Abril 2026
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    description: str
    supports_vision: bool = True
    supports_text: bool = True
    is_recommended: bool = False
    max_tokens: int = 4096
    cost_tier: str = "standard"  # "economy", "standard", "premium"


# Catálogo de modelos por provider
AVAILABLE_MODELS: dict[str, list[ModelInfo]] = {
    "claude": [
        ModelInfo(
            id="claude-sonnet-4-20250514",
            name="Claude Sonnet 4",
            provider="claude",
            description="Modelo mais recente da Anthropic. Recomendado para uso geral.",
            is_recommended=True,
            max_tokens=8192,
            cost_tier="standard",
        ),
        ModelInfo(
            id="claude-opus-4-5-20251101",
            name="Claude Opus 4.5",
            provider="claude",
            description="Modelo avançado para análises complexas.",
            max_tokens=8192,
            cost_tier="premium",
        ),
        ModelInfo(
            id="claude-3-5-haiku-20241022",
            name="Claude 3.5 Haiku",
            provider="claude",
            description="Modelo rápido e econômico.",
            max_tokens=4096,
            cost_tier="economy",
        ),
    ],
    "openai": [
        ModelInfo(
            id="gpt-4o",
            name="GPT-4o",
            provider="openai",
            description="Modelo multimodal mais recente. Excelente para imagens.",
            is_recommended=True,
            max_tokens=4096,
            cost_tier="standard",
        ),
        ModelInfo(
            id="gpt-4o-mini",
            name="GPT-4o Mini",
            provider="openai",
            description="Versão mais econômica do GPT-4o.",
            max_tokens=4096,
            cost_tier="economy",
        ),
        ModelInfo(
            id="gpt-4-turbo",
            name="GPT-4 Turbo",
            provider="openai",
            description="Alta capacidade, contexto de 128K tokens.",
            max_tokens=4096,
            cost_tier="premium",
        ),
    ],
    "gemini": [
        ModelInfo(
            id="gemini-3-flash",
            name="Gemini 3 Flash",
            provider="gemini",
            description="Modelo mais recente do Google. Rápido e multimodal.",
            is_recommended=True,
            max_tokens=8192,
            cost_tier="standard",
        ),
        ModelInfo(
            id="gemini-2.0-flash",
            name="Gemini 2.0 Flash",
            provider="gemini",
            description="Versão anterior, ainda muito capaz.",
            max_tokens=8192,
            cost_tier="standard",
        ),
        ModelInfo(
            id="gemini-1.5-pro",
            name="Gemini 1.5 Pro",
            provider="gemini",
            description="Modelo de alta capacidade com contexto de 1M tokens.",
            max_tokens=8192,
            cost_tier="standard",
        ),
    ],
}


def get_models_for_provider(provider: str) -> list[ModelInfo]:
    """Retorna lista de modelos disponíveis para um provider."""
    return AVAILABLE_MODELS.get(provider, [])


def get_recommended_model(provider: str) -> Optional[ModelInfo]:
    """Retorna o modelo recomendado para um provider."""
    models = get_models_for_provider(provider)
    for model in models:
        if model.is_recommended:
            return model
    return models[0] if models else None


def get_model_info(provider: str, model_id: str) -> Optional[ModelInfo]:
    """Retorna informações de um modelo específico."""
    models = get_models_for_provider(provider)
    for model in models:
        if model.id == model_id:
            return model
    return None


def get_all_models() -> dict[str, list[dict]]:
    """Retorna todos os modelos em formato serializável."""
    result = {}
    for provider, models in AVAILABLE_MODELS.items():
        result[provider] = [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "supports_vision": m.supports_vision,
                "supports_text": m.supports_text,
                "is_recommended": m.is_recommended,
                "max_tokens": m.max_tokens,
                "cost_tier": m.cost_tier,
            }
            for m in models
        ]
    return result
