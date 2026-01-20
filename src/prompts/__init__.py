"""
Modulo de prompts para traducao de documentos medicos
"""

from .base import PROMPT_BASE_LAUDO, PROMPT_BASE_RECEITA
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
from .selector import get_prompt_by_type

__all__ = [
    'PROMPT_BASE_LAUDO',
    'PROMPT_BASE_RECEITA',
    'PROMPT_EXAME_SANGUE',
    'PROMPT_EXAME_IMAGEM',
    'PROMPT_EXAME_URINA',
    'PROMPT_BIOPSIA',
    'PROMPT_LAUDO_OUTROS',
    'PROMPT_RECEITA_SIMPLES',
    'PROMPT_RECEITA_CONTROLADA',
    'PROMPT_RECEITA_ANTIBIOTICO',
    'get_prompt_by_type'
]
