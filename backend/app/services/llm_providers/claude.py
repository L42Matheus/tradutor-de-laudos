"""
Implementacao do provedor Anthropic (Claude)
"""
import anthropic
from anthropic import APIError, AuthenticationError, RateLimitError

from app.config import get_settings
from app.services.llm_providers.base import LLMProvider


class ClaudeProvider(LLMProvider):
    """
    Provider para modelos Claude da Anthropic

    Modelos suportados:
    - claude-sonnet-4-20250514 (recomendado)
    - claude-3-5-sonnet-20240620
    - claude-3-5-haiku-20241022 (mais econômico)
    - claude-3-opus-20240229 (mais capaz)
    """

    def __init__(self, api_key: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            raise ValueError("Anthropic API key não configurada")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature

    def translate_text(self, text: str, system_prompt: str, user_prompt: str, categoria: str) -> dict:
        """Traduz documento médico via texto"""
        doc_type = "receita médica" if categoria == "receita" else "laudo médico"

        user_message = f"""Analise o seguinte {doc_type} e forneça uma explicação completa:

{text}

{user_prompt}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            content = response.content[0].text
            if not content:
                raise ValueError("Resposta vazia do Claude")

            return self._parse_json_response(content)

        except AuthenticationError:
            raise ValueError("API key Anthropic inválida ou expirada")
        except RateLimitError:
            raise ValueError("Limite de requisições Anthropic atingido. Tente novamente em instantes.")
        except APIError as e:
            error_msg = str(e)
            if "not_found_error" in error_msg:
                raise ValueError(f"Modelo Claude não encontrado. Verifique a configuração: {self.model}")
            raise ValueError(f"Erro na API Claude: {error_msg}")
        except Exception as e:
            raise ValueError(f"Erro no Claude: {str(e)}")

    def translate_image(self, image_base64: str, media_type: str, system_prompt: str, user_prompt: str, categoria: str) -> dict:
        """Traduz documento médico via imagem"""
        doc_type = "receita médica" if categoria == "receita" else "laudo médico"

        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_base64
                }
            },
            {
                "type": "text",
                "text": f"""Analise a imagem do {doc_type} e forneça uma explicação completa.

{user_prompt}"""
            }
        ]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}]
            )

            content = response.content[0].text
            if not content:
                raise ValueError("Resposta vazia do Claude")

            return self._parse_json_response(content)

        except AuthenticationError:
            raise ValueError("API key Anthropic inválida ou expirada")
        except RateLimitError:
            raise ValueError("Limite de requisições Anthropic atingido. Tente novamente em instantes.")
        except APIError as e:
            error_msg = str(e)
            if "not_found_error" in error_msg:
                raise ValueError(f"Modelo Claude não encontrado. Verifique a configuração: {self.model}")
            raise ValueError(f"Erro na API Claude (imagem): {error_msg}")
        except Exception as e:
            raise ValueError(f"Erro no Claude (imagem): {str(e)}")
