"""
Implementacao do provedor OpenAI (GPT)
"""
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

from app.config import get_settings
from app.services.llm_providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Provider para modelos GPT da OpenAI

    Modelos suportados:
    - gpt-4o (recomendado - multimodal)
    - gpt-4o-mini (mais econômico)
    - gpt-4-turbo (alta capacidade)
    """

    def __init__(self, api_key: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key

        if not self.api_key:
            raise ValueError("OpenAI API key não configurada")

        self.client = OpenAI(api_key=self.api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature

    def translate_text(self, text: str, system_prompt: str, user_prompt: str, categoria: str) -> dict:
        """Traduz documento médico via texto"""
        doc_type = "receita médica" if categoria == "receita" else "laudo médico"

        user_message = f"""Analise o seguinte {doc_type} e forneça uma explicação completa:

{text}

{user_prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Resposta vazia do OpenAI")

            return self._parse_json_response(content)

        except AuthenticationError:
            raise ValueError("API key OpenAI inválida ou expirada")
        except RateLimitError:
            raise ValueError("Limite de requisições OpenAI atingido. Tente novamente em instantes.")
        except APIError as e:
            raise ValueError(f"Erro na API OpenAI: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro no OpenAI: {str(e)}")

    def translate_image(self, image_base64: str, media_type: str, system_prompt: str, user_prompt: str, categoria: str) -> dict:
        """Traduz documento médico via imagem"""
        doc_type = "receita médica" if categoria == "receita" else "laudo médico"

        # OpenAI espera data:image/jpeg;base64,xxxx
        image_url = f"data:{media_type};base64,{image_base64}"

        user_text = f"""Analise a imagem do {doc_type} e forneça uma explicação completa.

{user_prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            # Imagem primeiro, depois o texto
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "text",
                                "text": user_text
                            }
                        ]
                    }
                ]
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Resposta vazia do OpenAI")

            return self._parse_json_response(content)

        except AuthenticationError:
            raise ValueError("API key OpenAI inválida ou expirada")
        except RateLimitError:
            raise ValueError("Limite de requisições OpenAI atingido. Tente novamente em instantes.")
        except APIError as e:
            raise ValueError(f"Erro na API OpenAI (imagem): {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro no OpenAI (imagem): {str(e)}")
