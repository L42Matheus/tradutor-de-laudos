"""
Interface base para provedores de LLM
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMProvider(ABC):
    """Classe base abstrata para todos os provedores de LLM"""

    @abstractmethod
    def translate_text(
        self, 
        text: str, 
        system_prompt: str, 
        user_prompt: str, 
        categoria: str
    ) -> Dict[str, Any]:
        """Traduz um texto medico"""
        pass

    @abstractmethod
    def translate_image(
        self, 
        image_base64: str, 
        media_type: str, 
        system_prompt: str, 
        user_prompt: str, 
        categoria: str
    ) -> Dict[str, Any]:
        """Traduz um laudo a partir de imagem (Visao)"""
        pass

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Utilitario para extrair e validar JSON da resposta do LLM"""
        import json
        try:
            # Tenta extrair JSON de blocos de codigo markdown
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            data = json.loads(json_str)
            
            # Normalizacao basica
            return {
                "resumo": data.get("resumo", "Nao foi possivel gerar resumo"),
                "detalhado": data.get("detalhado", "Nao foi possivel gerar explicacao detalhada"),
                "entenda_facil": data.get("entenda_facil", "Nao foi possivel gerar explicacao simples"),
                "glossario": data.get("glossario", {}),
                "alertas": data.get("alertas", []),
                "is_saude_mental": data.get("is_saude_mental", False)
            }
        except Exception:
            # Fallback se o JSON falhar
            return {
                "resumo": "Erro ao processar resposta da IA",
                "detalhado": response_text,
                "entenda_facil": "Tente novamente ou use outro provedor.",
                "glossario": {},
                "alertas": ["Erro de formatacao na resposta da IA"],
                "is_saude_mental": False
            }
