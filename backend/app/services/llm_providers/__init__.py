"""
LLM Providers - Abstração para múltiplos modelos de IA
Suporta: Claude (Anthropic), GPT (OpenAI), Gemini (Google)
"""

from app.services.llm_providers.base import LLMProvider
from app.services.llm_providers.router import LLMRouter
from app.services.llm_providers.claude import ClaudeProvider
from app.services.llm_providers.openai import OpenAIProvider
from app.services.llm_providers.gemini import GeminiProvider
from app.services.llm_providers.models import (
    AVAILABLE_MODELS,
    ModelInfo,
    get_all_models,
    get_model_info,
    get_models_for_provider,
    get_recommended_model,
)

__all__ = [
    "LLMProvider",
    "LLMRouter",
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "AVAILABLE_MODELS",
    "ModelInfo",
    "get_all_models",
    "get_model_info",
    "get_models_for_provider",
    "get_recommended_model",
]
