"""
Modulo de configuracoes
"""

from .settings import (
    DocumentCategory,
    TIPOS_LAUDO,
    TIPOS_RECEITA,
    ALLOWED_FILE_TYPES,
    IMAGE_MIME_TYPES,
    CLAUDE_MODEL,
    MAX_TOKENS,
    TEMPERATURE
)

__all__ = [
    'DocumentCategory',
    'TIPOS_LAUDO',
    'TIPOS_RECEITA',
    'ALLOWED_FILE_TYPES',
    'IMAGE_MIME_TYPES',
    'CLAUDE_MODEL',
    'MAX_TOKENS',
    'TEMPERATURE'
]
