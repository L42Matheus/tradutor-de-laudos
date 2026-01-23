"""
Servico de traducao de documentos medicos
Suporta laudos e receitas, em texto e imagem
Com cache integrado para economizar chamadas a API
"""

import json
import anthropic

from src.config import (
    DocumentCategory,
    CLAUDE_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    CACHE_ENABLED
)
from src.prompts import get_prompt_by_type
from src.services.cache import get_cache, CacheKeyGenerator


class MedicalTranslator:
    """Tradutor de documentos medicos (laudos e receitas)"""

    def __init__(self, api_key: str, use_cache: bool = CACHE_ENABLED):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = CLAUDE_MODEL
        self.use_cache = use_cache
        self._cache = get_cache() if use_cache else None

    def translate_text(self, text: str, tipo: str, categoria: str = DocumentCategory.LAUDO) -> dict:
        """
        Traduz documento medico em texto

        Args:
            text: Texto do documento (ja anonimizado)
            tipo: Tipo especifico do documento
            categoria: 'laudo' ou 'receita'

        Returns:
            dict com resumo, explicacao detalhada, glossario e alertas
        """
        # Verifica cache primeiro
        cache_key = None
        if self.use_cache and self._cache:
            cache_key = CacheKeyGenerator.generate(text, tipo, categoria)
            cached_result = self._cache.get(cache_key)
            if cached_result:
                cached_result['from_cache'] = True
                return cached_result

        system_prompt = get_prompt_by_type(tipo, categoria)
        user_prompt = self._get_user_prompt(categoria)
        doc_type = "receita medica" if categoria == DocumentCategory.RECEITA else "laudo medico"

        user_message = f"""Analise o seguinte {doc_type} e forneca uma explicacao completa:

{text}

{user_prompt}"""

        result = self._call_api(system_prompt, user_message)

        # Salva no cache
        if self.use_cache and self._cache and cache_key:
            self._cache.set(cache_key, result)

        result['from_cache'] = False
        return result

    def translate_image(self, image_base64: str, media_type: str, tipo: str,
                       categoria: str = DocumentCategory.LAUDO) -> dict:
        """
        Traduz documento medico a partir de imagem

        Args:
            image_base64: Imagem em base64
            media_type: Tipo MIME da imagem
            tipo: Tipo especifico do documento
            categoria: 'laudo' ou 'receita'

        Returns:
            dict com resumo, explicacao detalhada, glossario e alertas
        """
        # Verifica cache primeiro
        cache_key = None
        if self.use_cache and self._cache:
            cache_key = CacheKeyGenerator.generate_from_image(image_base64, tipo, categoria)
            cached_result = self._cache.get(cache_key)
            if cached_result:
                cached_result['from_cache'] = True
                return cached_result

        system_prompt = get_prompt_by_type(tipo, categoria)
        user_prompt = self._get_user_prompt(categoria)
        doc_type = "receita medica" if categoria == DocumentCategory.RECEITA else "laudo medico"

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
                "text": f"""Analise a imagem do {doc_type} acima e forneca uma explicacao completa.

{user_prompt}"""
            }
        ]

        result = self._call_api_with_image(system_prompt, user_content)

        # Salva no cache
        if self.use_cache and self._cache and cache_key:
            self._cache.set(cache_key, result)

        result['from_cache'] = False
        return result

    def _get_user_prompt(self, categoria: str) -> str:
        """Retorna o prompt de instrucao baseado na categoria"""
        if categoria == DocumentCategory.RECEITA:
            return """Por favor, forneca:
1. Um resumo simples de todos os medicamentos prescritos
2. Explicacao detalhada de cada medicamento (para que serve, como tomar)
3. Explicacao super simples, como se fosse para uma crianca de 10 anos ou alguem que nunca estudou medicina (use analogias do dia a dia, evite termos tecnicos)
4. Um glossario dos termos tecnicos encontrados
5. Alertas importantes (interacoes, efeitos colaterais, cuidados)

Formato da resposta em JSON:
{
    "resumo": "resumo dos medicamentos",
    "detalhado": "explicacao detalhada de cada medicamento",
    "entenda_facil": "explicacao como se fosse para crianca, bem simples e com analogias",
    "glossario": "glossario de termos",
    "alertas": "avisos importantes ou null"
}"""
        else:
            return """Por favor, forneca:
1. Um resumo em linguagem simples (como se explicasse para alguem sem conhecimento medico)
2. Uma explicacao mais detalhada de cada parte importante
3. Explicacao super simples, como se fosse para uma crianca de 10 anos ou alguem que nunca estudou medicina (use analogias do dia a dia, evite termos tecnicos)
4. Um glossario dos principais termos tecnicos encontrados
5. Alertas caso haja algo que exija atencao medica urgente

Formato da resposta em JSON:
{
    "resumo": "texto do resumo simples",
    "detalhado": "explicacao detalhada",
    "entenda_facil": "explicacao como se fosse para crianca, bem simples e com analogias",
    "glossario": "glossario de termos",
    "alertas": "avisos importantes ou null"
}"""

    def _call_api(self, system_prompt: str, user_message: str) -> dict:
        """Chama a API do Claude com texto"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = response.content[0].text
            return self._parse_response(response_text)

        except Exception as e:
            raise Exception(f"Erro ao processar com a API: {str(e)}")

    def _call_api_with_image(self, system_prompt: str, user_content: list) -> dict:
        """Chama a API do Claude com imagem"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_content}
                ]
            )

            response_text = response.content[0].text
            return self._parse_response(response_text)

        except Exception as e:
            raise Exception(f"Erro ao processar imagem com a API: {str(e)}")

    def _parse_response(self, response_text: str) -> dict:
        """Faz parse da resposta JSON do Claude"""
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
                json_text = response_text

            resultado = json.loads(json_text)

            return {
                'resumo': resultado.get('resumo', 'Nao foi possivel gerar resumo'),
                'detalhado': resultado.get('detalhado', 'Nao foi possivel gerar explicacao detalhada'),
                'entenda_facil': resultado.get('entenda_facil', 'Nao foi possivel gerar explicacao simples'),
                'glossario': resultado.get('glossario', 'Nao foi possivel gerar glossario'),
                'alertas': resultado.get('alertas')
            }

        except json.JSONDecodeError:
            return {
                'resumo': response_text[:500] + "...",
                'detalhado': response_text,
                'glossario': "Nao foi possivel gerar glossario",
                'alertas': None
            }
