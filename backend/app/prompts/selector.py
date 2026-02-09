"""
Seletor de prompts baseado em tipo e categoria
"""

from app.models.enums import DocumentCategory, LaudoType, ReceitaType, SaudeMentalType
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
from .saude_mental import (
    PROMPT_ANTIDEPRESSIVO,
    PROMPT_ANSIOLITICO,
    PROMPT_LAUDO_PSIQUIATRICO,
    PROMPT_SAUDE_MENTAL_OUTROS
)


def get_prompt_by_type(tipo: str, categoria: str = DocumentCategory.LAUDO) -> str:
    """
    Retorna o prompt adequado baseado no tipo e categoria
    """
    if categoria == DocumentCategory.RECEITA:
        return _get_receita_prompt(tipo)
    elif categoria == DocumentCategory.SAUDE_MENTAL:
        return _get_saude_mental_prompt(tipo)
    else:
        return _get_laudo_prompt(tipo)


def _get_laudo_prompt(tipo: str) -> str:
    """Retorna prompt para laudos"""
    tipo_map = {
        # Enum values
        LaudoType.EXAME_SANGUE: PROMPT_EXAME_SANGUE,
        LaudoType.EXAME_IMAGEM: PROMPT_EXAME_IMAGEM,
        LaudoType.EXAME_URINA: PROMPT_EXAME_URINA,
        LaudoType.BIOPSIA: PROMPT_BIOPSIA,
        LaudoType.OUTROS: PROMPT_LAUDO_OUTROS,
        # String values
        "exame_sangue": PROMPT_EXAME_SANGUE,
        "exame_imagem": PROMPT_EXAME_IMAGEM,
        "exame_urina": PROMPT_EXAME_URINA,
        "biopsia": PROMPT_BIOPSIA,
        "outros": PROMPT_LAUDO_OUTROS,
        # Legacy string values (Portuguese labels)
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
        # Enum values
        ReceitaType.SIMPLES: PROMPT_RECEITA_SIMPLES,
        ReceitaType.CONTROLADA: PROMPT_RECEITA_CONTROLADA,
        ReceitaType.ANTIBIOTICO: PROMPT_RECEITA_ANTIBIOTICO,
        # String values
        "simples": PROMPT_RECEITA_SIMPLES,
        "controlada": PROMPT_RECEITA_CONTROLADA,
        "antibiotico": PROMPT_RECEITA_ANTIBIOTICO,
        # Legacy string values
        "Receita Simples": PROMPT_RECEITA_SIMPLES,
        "Receita de Controle Especial": PROMPT_RECEITA_CONTROLADA,
        "Receita de Antibiotico": PROMPT_RECEITA_ANTIBIOTICO
    }
    return tipo_map.get(tipo, PROMPT_RECEITA_SIMPLES)


def _get_saude_mental_prompt(tipo: str) -> str:
    """Retorna prompt para saude mental"""
    tipo_map = {
        # Enum values
        SaudeMentalType.ANTIDEPRESSIVO: PROMPT_ANTIDEPRESSIVO,
        SaudeMentalType.ANSIOLITICO: PROMPT_ANSIOLITICO,
        SaudeMentalType.LAUDO_PSIQUIATRICO: PROMPT_LAUDO_PSIQUIATRICO,
        SaudeMentalType.OUTROS: PROMPT_SAUDE_MENTAL_OUTROS,
        # String values
        "antidepressivo": PROMPT_ANTIDEPRESSIVO,
        "ansiolitico": PROMPT_ANSIOLITICO,
        "laudo_psiquiatrico": PROMPT_LAUDO_PSIQUIATRICO,
        "outros": PROMPT_SAUDE_MENTAL_OUTROS,
        # Legacy string values
        "Receita de Antidepressivo": PROMPT_ANTIDEPRESSIVO,
        "Receita de Ansiolitico": PROMPT_ANSIOLITICO,
        "Laudo Psiquiatrico": PROMPT_LAUDO_PSIQUIATRICO,
        "Outro": PROMPT_SAUDE_MENTAL_OUTROS
    }
    return tipo_map.get(tipo, PROMPT_SAUDE_MENTAL_OUTROS)
