"""
Servico de traducao com extracao de metadados epidemiologicos.
Realiza traducao e extracao de metadados em uma unica chamada LLM.
"""
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import anthropic

from app.config import get_settings
from app.services.cache import CacheKeyGenerator, get_cache


settings = get_settings()


@dataclass(frozen=True)
class AlertRule:
    name: str
    required_groups: tuple[tuple[str, ...], ...]
    alerts: tuple[str, ...]

SYSTEM_PROMPT = """Voce e um assistente medico especializado. Dado um laudo medico, retorne APENAS um JSON valido (sem markdown, sem explicacoes) com esta estrutura exata:
{
  "resumo": "resumo claro e relativamente completo, em linguagem simples para paciente leigo, com cerca de 4 a 6 frases e cobrindo os principais achados, localizacao, gravidade e impacto pratico",
  "detalhado": "explicacao mais completa dos achados, em linguagem acessivel, preservando os pontos clinicos importantes",
  "entenda_facil": "explicacao muito simples, como se fosse para uma crianca ou para quem nunca viu esse tema, usando analogias do dia a dia e passo a passo quando fizer sentido",
  "texto_traduzido": "versao do laudo em linguagem clara e acessivel para paciente leigo, com empatia",
  "glossario": {
    "termo_tecnico_1": "explicacao simples e clara para paciente leigo",
    "termo_tecnico_2": "explicacao simples e clara para paciente leigo"
  },
  "alertas": ["alerta importante 1", "alerta importante 2"],
  "condicao_categoria": "uma de: cardiovascular | respiratorio | neurologico | oncologico | ortopedico | endocrinologico | outro",
  "faixa_etaria": "uma de: 0-17 | 18-30 | 31-45 | 46-60 | 60+ | nao_informado",
  "data_laudo": "YYYY-MM se encontrada no texto, senao null",
  "nome_clinica": "nome exato da clinica ou hospital se mencionado no laudo, senao null"
}

IMPORTANTE sobre o glossario:
- SEMPRE inclua pelo menos 3-5 termos tecnicos encontrados no laudo
- Inclua diagnosticos, exames, medicamentos, procedimentos, siglas medicas
- Cada termo deve ter uma explicacao clara e acessivel para leigos

IMPORTANTE sobre os blocos de texto:
- "resumo" deve ser claro, um pouco mais desenvolvido e suficiente para o paciente entender os pontos principais sem precisar abrir os outros blocos
- "resumo" NAO deve ser seco ou telegráfico; ele precisa formar uma explicacao corrida e util para o paciente
- "resumo" deve mencionar, quando estiver no laudo: onde esta o achado, o grau/gravidade, o efeito funcional e a orientacao geral de acompanhamento
- "detalhado" deve expandir os principais achados de forma organizada
- "entenda_facil" NAO pode repetir o resumo; deve usar comparacoes e linguagem bem didatica
- "texto_traduzido" pode ser igual ao resumo ampliado, mas deve continuar natural para o paciente
- "alertas" deve ser uma lista vazia quando nao houver alerta relevante
- NAO mencione "categoria epidemiologica", "faixa etaria estimada" ou classificacoes internas nos textos visiveis ao paciente

Nao inclua nome do paciente, CPF, data de nascimento ou qualquer dado pessoal identificavel na resposta."""


CRITICAL_ALERT_RULES: tuple[AlertRule, ...] = (
    AlertRule(
        name="neuro_mass_effect",
        required_groups=(
            ("cerebr", "cranio", "crânio", "intracran", "frontopariet", "frontal", "parietal", "temporal", "occipital"),
            ("lesao expansiva", "lesão expansiva", "massa", "tumor", "nodulo expansivo", "nódulo expansivo"),
            ("edema", "compress", "efeito de massa", "desvio", "deslocamento", "linha media", "linha média", "ventriculo lateral", "ventrículo lateral", "hernia", "hérnia"),
        ),
        alerts=(
            "Este exame sugere um achado cerebral importante com pressao sobre estruturas do cerebro e requer avaliacao medica urgente, idealmente neurologica ou neurocirurgica.",
            "Se houver dor de cabeca intensa, vomitos, sonolencia, confusao, fraqueza, convulsoes ou piora neurologica, procure atendimento de urgencia imediatamente.",
        ),
    ),
    AlertRule(
        name="neuro_hemorrhage",
        required_groups=(
            ("cerebr", "cranio", "crânio", "intracran"),
            ("hemorrag", "hematoma", "sangramento"),
        ),
        alerts=(
            "Ha indicio de sangramento em contexto neurologico. Isso exige avaliacao medica urgente.",
        ),
    ),
    AlertRule(
        name="acute_stroke",
        required_groups=(
            ("avc", "isquemi", "infarto cerebral", "oclusao", "oclusão", "trombo"),
            ("agud", "recente", "territorio", "território"),
        ),
        alerts=(
            "O exame pode indicar um evento neurologico agudo. Procure avaliacao medica urgente, especialmente se houver perda de forca, fala alterada, assimetria facial ou confusao.",
        ),
    ),
    AlertRule(
        name="pulmonary_urgent",
        required_groups=(
            ("pulm", "torax", "tórax", "pleur"),
            ("embolia", "pneumotorax", "pneumotórax", "derrame pleural volumoso", "insuficiencia respiratoria", "insuficiência respiratória"),
        ),
        alerts=(
            "Ha um achado toracico potencialmente grave. Se houver falta de ar, dor no peito, labios arroxeados ou piora rapida, procure atendimento de urgencia.",
        ),
    ),
    AlertRule(
        name="cardiovascular_urgent",
        required_groups=(
            ("aorta", "cardi", "coronar", "miocard", "vascular"),
            ("dissecc", "dissecção", "aneurisma", "oclus", "oclusão", "infarto", "trombo"),
        ),
        alerts=(
            "O exame descreve um achado cardiovascular potencialmente grave que precisa de avaliacao medica urgente.",
        ),
    ),
)


def _extrair_json_da_resposta(texto: str) -> Optional[Dict[str, Any]]:
    """
    Tenta extrair JSON da resposta do LLM.
    Primeiro tenta parse direto, depois regex para blocos de codigo.
    """
    texto = texto.strip()

    if texto.startswith("```"):
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", texto)
        if match:
            texto = match.group(1).strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", texto)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def _validar_estrutura(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida e normaliza a estrutura do JSON extraido.
    """
    categorias_validas = [
        "cardiovascular",
        "respiratorio",
        "neurologico",
        "oncologico",
        "ortopedico",
        "endocrinologico",
        "outro",
    ]

    faixas_validas = ["0-17", "18-30", "31-45", "46-60", "60+", "nao_informado"]

    resultado = {
        "resumo": data.get("resumo", ""),
        "detalhado": data.get("detalhado", ""),
        "entenda_facil": data.get("entenda_facil", ""),
        "texto_traduzido": data.get("texto_traduzido", ""),
        "glossario": data.get("glossario", {}),
        "alertas": data.get("alertas", []),
        "condicao_categoria": data.get("condicao_categoria", "outro"),
        "faixa_etaria": data.get("faixa_etaria", "nao_informado"),
        "data_laudo": data.get("data_laudo"),
        "nome_clinica": data.get("nome_clinica"),
    }

    if not isinstance(resultado["glossario"], dict):
        resultado["glossario"] = {}

    if not isinstance(resultado["alertas"], list):
        if isinstance(resultado["alertas"], str) and resultado["alertas"].strip():
            resultado["alertas"] = [resultado["alertas"].strip()]
        else:
            resultado["alertas"] = []

    resumo = (resultado["resumo"] or "").strip()
    detalhado = (resultado["detalhado"] or "").strip()
    entenda_facil = (resultado["entenda_facil"] or "").strip()
    texto_traduzido = (resultado["texto_traduzido"] or "").strip()

    if not resumo:
        resumo = texto_traduzido
    if not texto_traduzido:
        texto_traduzido = resumo
    if not detalhado:
        detalhado = texto_traduzido
    if not entenda_facil:
        entenda_facil = resumo

    resumo = _normalizar_resumo_curto(resumo, texto_traduzido, detalhado)

    resultado["resumo"] = resumo
    resultado["detalhado"] = detalhado
    resultado["entenda_facil"] = entenda_facil
    resultado["texto_traduzido"] = texto_traduzido

    if resultado["condicao_categoria"] not in categorias_validas:
        resultado["condicao_categoria"] = "outro"

    if resultado["faixa_etaria"] not in faixas_validas:
        resultado["faixa_etaria"] = "nao_informado"

    if resultado["data_laudo"] and not re.match(r"^\d{4}-\d{2}$", str(resultado["data_laudo"])):
        resultado["data_laudo"] = None

    return resultado


def _normalizar_resumo_curto(resumo: str, texto_traduzido: str, detalhado: str) -> str:
    candidatos = [resumo, texto_traduzido, detalhado]

    def pontuacao(texto: str) -> tuple[int, int]:
        texto_limpo = (texto or "").strip()
        frases = len(re.findall(r"[.!?]", texto_limpo))
        return (len(texto_limpo), frases)

    resumo_limpo = resumo.strip()
    tamanho_resumo, frases_resumo = pontuacao(resumo_limpo)
    if tamanho_resumo >= 280 and frases_resumo >= 3:
        return resumo_limpo

    melhor = max(candidatos, key=pontuacao).strip()
    return melhor or resumo_limpo


def _adicionar_alertas_criticos(texto_original: str, resultado: Dict[str, Any]) -> Dict[str, Any]:
    texto = (texto_original or "").lower()
    alertas = [
        alerta.strip()
        for alerta in resultado.get("alertas", [])
        if isinstance(alerta, str) and alerta.strip()
    ]

    def add_alerta(alerta: str) -> None:
        if alerta not in alertas:
            alertas.append(alerta)

    tem_contexto_cerebral = any(
        termo in texto
        for termo in [
            "cerebr",
            "cranio",
            "crânio",
            "intracran",
            "frontopariet",
            "frontal",
            "parietal",
            "temporal",
            "occipital",
        ]
    )
    tem_lesao_expansiva = any(
        termo in texto
        for termo in [
            "lesao expansiva",
            "lesão expansiva",
            "massa",
            "tumor",
            "nodulo expansivo",
            "nódulo expansivo",
        ]
    )
    tem_efeito_massa = any(
        termo in texto
        for termo in [
            "edema",
            "compress",
            "efeito de massa",
            "desvio",
            "deslocamento",
            "linha media",
            "linha média",
            "ventriculo lateral",
            "ventrículo lateral",
            "hernia",
            "hérnia",
        ]
    )

    if tem_contexto_cerebral and tem_lesao_expansiva and tem_efeito_massa:
        add_alerta(
            "Este exame sugere um achado cerebral importante com pressao sobre estruturas do cerebro e requer avaliacao medica urgente, idealmente neurologica ou neurocirurgica."
        )
        add_alerta(
            "Se houver dor de cabeca intensa, vomitos, sonolencia, confusao, fraqueza, convulsoes ou piora neurologica, procure atendimento de urgencia imediatamente."
        )

    if "hemorrag" in texto or "sangramento intracran" in texto:
        add_alerta(
            "Ha indicio de sangramento em um contexto neurologico. Isso exige avaliacao medica urgente."
        )

    resultado["alertas"] = alertas
    return resultado


async def processar_laudo(texto: str) -> Dict[str, Any]:
    """
    Processa um laudo medico: traduz e extrai metadados em uma unica chamada LLM.

    Returns:
        Dict com resumo, detalhado, entenda_facil, texto_traduzido, glossario, alertas,
        condicao_categoria, faixa_etaria, data_laudo e nome_clinica.
    """
    cache = get_cache()
    cache_key = CacheKeyGenerator.generate(
        texto,
        "laudo",
        "epidemio",
        namespace="traducao_epidemio_v5",
    )

    cached = cache.get(cache_key)
    if cached:
        cached["from_cache"] = True
        return cached

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Processe o seguinte laudo medico:\n\n{texto}",
            }
        ],
    )

    resposta_texto = response.content[0].text
    dados = _extrair_json_da_resposta(resposta_texto)

    if not dados:
        raise ValueError(
            f"Nao foi possivel extrair JSON valido da resposta: {resposta_texto[:200]}..."
        )

    resultado = _validar_estrutura(dados)
    resultado = _adicionar_alertas_criticos(texto, resultado)
    resultado["from_cache"] = False

    cache.set(cache_key, resultado)

    return resultado


def extrair_faixa_etaria_regex(texto: str) -> Optional[str]:
    """
    Tenta extrair faixa etaria do texto usando regex antes de usar LLM.
    Util como fallback ou para pre-processamento.
    """
    padroes = [
        r"(\d+)\s*anos?\s*(?:de\s*)?idade",
        r"idade[:\s]+(\d+)",
        r"paciente[:\s]+\d+[,\s]+(\d+)\s*anos?",
        r"(\d+)\s*a(?:nos)?\.?$",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            idade = int(match.group(1))

            if idade <= 17:
                return "0-17"
            if idade <= 30:
                return "18-30"
            if idade <= 45:
                return "31-45"
            if idade <= 60:
                return "46-60"
            return "60+"

    return None
