"""
Implementacao do provedor Google (Gemini)
"""
import base64
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config import get_settings
from app.services.llm_providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Provider para modelos Gemini do Google

    Modelos suportados:
    - gemini-1.5-pro (recomendado)
    - gemini-1.5-flash (mais rápido)
    - gemini-2.0-flash-exp (experimental)
    """

    # Configuração de segurança para permitir conteúdo médico
    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    def __init__(self, api_key: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.google_api_key

        if not self.api_key:
            raise ValueError("Google API key não configurada")

        genai.configure(api_key=self.api_key)
        self.model_name = settings.gemini_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens

    def translate_text(self, text: str, system_prompt: str, user_prompt: str, categoria: str) -> dict:
        """Traduz documento médico via texto"""
        doc_type = "receita médica" if categoria == "receita" else "laudo médico"

        full_prompt = f"""{system_prompt}

Analise o seguinte {doc_type} e forneça uma explicação completa:

{text}

{user_prompt}"""

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=self.SAFETY_SETTINGS,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )

            response = model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Resposta vazia do Gemini")

            return self._parse_json_response(response.text)

        except Exception as e:
            error_msg = str(e)
            if "blocked" in error_msg.lower():
                raise ValueError(f"Conteúdo bloqueado pelo Gemini. Tente outro provider.")
            raise ValueError(f"Erro no Gemini: {error_msg}")

    def translate_image(self, image_base64: str, media_type: str, system_prompt: str, user_prompt: str, categoria: str) -> dict:
        """Traduz documento médico via imagem"""
        doc_type = "receita médica" if categoria == "receita" else "laudo médico"

        # Decodifica a imagem
        try:
            image_data = base64.b64decode(image_base64)
        except Exception:
            raise ValueError("Imagem inválida (base64 corrompido)")

        full_prompt = f"""{system_prompt}

Analise a imagem do {doc_type} e forneça uma explicação completa.

{user_prompt}"""

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=self.SAFETY_SETTINGS,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )

            # Gemini espera a imagem como dict com mime_type e data
            image_part = {
                "mime_type": media_type,
                "data": image_data
            }

            response = model.generate_content([image_part, full_prompt])

            if not response.text:
                raise ValueError("Resposta vazia do Gemini")

            return self._parse_json_response(response.text)

        except Exception as e:
            error_msg = str(e)
            if "blocked" in error_msg.lower():
                raise ValueError(f"Conteúdo bloqueado pelo Gemini. Tente outro provider.")
            raise ValueError(f"Erro no Gemini (imagem): {error_msg}")
