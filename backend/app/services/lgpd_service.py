"""
Serviço de conformidade LGPD para sanitização de metadados epidemiológicos.
Garante que nenhum dado pessoal identificável (PII) seja armazenado.
"""
import re
from datetime import date
from typing import Optional, Dict, Any


CAMPOS_PII = [
    "nome", "nome_paciente", "paciente",
    "cpf", "rg", "cns", "sus",
    "endereco", "endereco_completo", "rua", "bairro", "cep",
    "telefone", "celular", "email",
    "data_nascimento", "nascimento",
    "nome_mae", "nome_pai", "filiacao"
]

PADROES_PII = [
    r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
    r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
    r'\b\d{15}\b',
    r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
    r'\b\(\d{2}\)\s*\d{4,5}-?\d{4}\b',
    r'\b\d{5}-?\d{3}\b',
]


def _contem_pii(texto: str) -> bool:
    """Verifica se um texto contém padrões de PII."""
    for padrao in PADROES_PII:
        if re.search(padrao, texto):
            return True
    return False


def _converter_mes_ano(data_str: Optional[str]) -> Optional[date]:
    """
    Converte string YYYY-MM para date do primeiro dia do mês.

    Args:
        data_str: String no formato YYYY-MM

    Returns:
        date(YYYY, MM, 1) ou None
    """
    if not data_str:
        return None

    match = re.match(r'^(\d{4})-(\d{2})$', data_str)
    if match:
        ano = int(match.group(1))
        mes = int(match.group(2))

        if 2000 <= ano <= 2100 and 1 <= mes <= 12:
            return date(ano, mes, 1)

    return None


def sanitizar_metadados(
    extracao: Dict[str, Any],
    geo: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Sanitiza metadados extraídos para garantir conformidade LGPD.

    Regras:
    - Descarta: nome_clinica, qualquer campo com PII
    - Mantém apenas: municipio, estado, lat, lon, condicao_categoria, faixa_etaria, mes_ano
    - Se geo for None: retorna None (sem localização não grava)

    Args:
        extracao: Dict retornado por processar_laudo()
        geo: Dict retornado por geocodificar() ou None

    Returns:
        Dict sanitizado com metadados epidemiológicos ou None
    """
    if not geo:
        return None

    if not all(k in geo for k in ["municipio", "estado", "lat", "lon"]):
        return None

    for campo in CAMPOS_PII:
        if campo in extracao:
            valor = extracao[campo]
            if valor and isinstance(valor, str) and _contem_pii(valor):
                return None

    condicao = extracao.get("condicao_categoria", "outro")
    categorias_validas = [
        "cardiovascular", "respiratorio", "neurologico",
        "oncologico", "ortopedico", "endocrinologico", "outro"
    ]
    if condicao not in categorias_validas:
        condicao = "outro"

    faixa = extracao.get("faixa_etaria", "nao_informado")
    faixas_validas = ["0-17", "18-30", "31-45", "46-60", "60+", "nao_informado"]
    if faixa not in faixas_validas:
        faixa = "nao_informado"

    mes_ano = _converter_mes_ano(extracao.get("data_laudo"))
    if not mes_ano:
        mes_ano = date.today().replace(day=1)

    return {
        "municipio": geo["municipio"],
        "estado": geo["estado"][:2].upper(),
        "lat": round(float(geo["lat"]), 6),
        "lon": round(float(geo["lon"]), 6),
        "condicao_categoria": condicao,
        "faixa_etaria": faixa,
        "mes_ano": mes_ano
    }


def validar_texto_sem_pii(texto: str) -> bool:
    """
    Valida se um texto está livre de PII antes de armazenar.

    Args:
        texto: Texto a ser validado

    Returns:
        True se o texto está livre de PII detectável
    """
    return not _contem_pii(texto)


def remover_pii_texto(texto: str) -> str:
    """
    Remove padrões de PII de um texto.
    Útil para sanitizar texto_traduzido antes de armazenar.

    Args:
        texto: Texto original

    Returns:
        Texto com PII substituído por [REMOVIDO]
    """
    resultado = texto

    for padrao in PADROES_PII:
        resultado = re.sub(padrao, "[REMOVIDO]", resultado)

    return resultado
