"""
Seletor de prompts baseado em tipo e categoria
"""

from src.config import DocumentCategory
from .laudos import (
    PROMPT_EXAME_SANGUE,
    PROMPT_EXAME_IMAGEM,
    PROMPT_EXAME_URINA,
    PROMPT_BIOPSIA,
    PROMPT_LAUDO_OUTROS
)
from .receitas import (
    PROMPT_RECEITA_SIMPLES,
    PROMPT_RECEITA_CONTROLADA,
    PROMPT_RECEITA_ANTIBIOTICO
)


def get_prompt_by_type(tipo: str, categoria: str = DocumentCategory.LAUDO) -> str:
    """
    Retorna o prompt adequado baseado no tipo e categoria

    Args:
        tipo: String com o tipo especifico
        categoria: 'laudo' ou 'receita'

    Returns:
        String com o prompt do sistema
    """
    if categoria == DocumentCategory.RECEITA:
        return _get_receita_prompt(tipo)
    else:
        return _get_laudo_prompt(tipo)


def _get_laudo_prompt(tipo: str) -> str:
    """Retorna prompt para laudos"""
    tipo_map = {
        "Exame de Sangue": PROMPT_EXAME_SANGUE,
        "Exame de Imagem (RX, TC, RM)": PROMPT_EXAME_IMAGEM,
        "Exame de Urina": PROMPT_EXAME_URINA,
        "Biopsia/Patologia": PROMPT_BIOPSIA,
        "Outro": PROMPT_LAUDO_OUTROS
    }
    return tipo_map.get(tipo, PROMPT_LAUDO_OUTROS)


def _get_receita_prompt(tipo: str) -> str:
    """Retorna prompt para receitas"""
    tipo_map = {
        "Receita Simples": PROMPT_RECEITA_SIMPLES,
        "Receita de Controle Especial": PROMPT_RECEITA_CONTROLADA,
        "Receita de Antibiotico": PROMPT_RECEITA_ANTIBIOTICO
    }
    return tipo_map.get(tipo, PROMPT_RECEITA_SIMPLES)
