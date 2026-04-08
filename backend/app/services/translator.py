"""
Servico de traducao de documentos medicos
Suporta laudos e receitas, em texto e imagem
Com roteamento dinâmico de LLM (Claude, OpenAI, Gemini)
"""

import json
from app.config import get_settings
from app.models.enums import DocumentCategory
from app.prompts import get_prompt_by_type
from app.services.cache import get_cache, CacheKeyGenerator
from app.services.llm_providers.router import LLMRouter


class MedicalTranslator:
    """Tradutor de documentos medicos (laudos e receitas)"""

    def __init__(self, provider_name: str = None, use_cache: bool = None):
        settings = get_settings()
        self.provider = LLMRouter.get_provider(provider_name)
        self.use_cache = use_cache if use_cache is not None else settings.cache_enabled
        self._cache = get_cache() if self.use_cache else None

    def translate_text(self, text: str, tipo: str, categoria: str = DocumentCategory.LAUDO) -> dict:
        """Traduz documento medico em texto com roteamento dinamico"""
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

        result = self.provider.translate_text(
            text=text,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            categoria=categoria
        )

        # Salva no cache
        if self.use_cache and self._cache and cache_key:
            self._cache.set(cache_key, result)

        result['from_cache'] = False
        return result

    def translate_image(self, image_base64: str, media_type: str, tipo: str,
                       categoria: str = DocumentCategory.LAUDO) -> dict:
        """Traduz documento medico a partir de imagem com roteamento dinamico"""
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

        result = self.provider.translate_image(
            image_base64=image_base64,
            media_type=media_type,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            categoria=categoria
        )

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
6. Identifique se algum medicamento e para saude mental (ansiedade, depressao, transtornos psiquiatricos, insonia, etc)

Formato da resposta em JSON:
{
    "resumo": "resumo dos medicamentos",
    "detalhado": "explicacao detalhada de cada medicamento",
    "entenda_facil": "explicacao como se fosse para crianca, bem simples e com analogias",
    "glossario": {"termo1": "definicao1", "termo2": "definicao2"},
    "alertas": ["alerta1", "alerta2"] ou [],
    "is_saude_mental": true ou false
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
    "glossario": {"termo1": "definicao1", "termo2": "definicao2"},
    "alertas": ["alerta1", "alerta2"] ou [],
    "is_saude_mental": false
}"""
