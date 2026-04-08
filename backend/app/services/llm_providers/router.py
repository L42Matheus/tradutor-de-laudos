"""
Roteador para selecionar o provedor de LLM correto
"""
from typing import Optional
from app.config import get_settings
from app.services.llm_providers.base import LLMProvider
from app.services.llm_providers.claude import ClaudeProvider
from app.services.llm_providers.openai import OpenAIProvider
from app.services.llm_providers.gemini import GeminiProvider


class LLMRouter:
    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> LLMProvider:
        settings = get_settings()
        
        # Fallback para o default se nao informado ou nao habilitado
        if not provider_name or provider_name not in settings.enabled_providers:
            provider_name = "claude" # Default do sistema
            
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "gemini":
            return GeminiProvider()
        else:
            return ClaudeProvider()
