"""
Modulo de servicos
"""

from .translator import MedicalTranslator
from .validator import DocumentValidator
from .anonymizer import anonymize_text
from .cache import get_cache, InMemoryCache, CacheKeyGenerator
from .usage_limiter import (
    can_translate,
    increment_usage,
    show_usage_status,
    show_limit_reached,
    get_remaining_translations
)

__all__ = [
    'MedicalTranslator',
    'DocumentValidator',
    'anonymize_text',
    'get_cache',
    'InMemoryCache',
    'CacheKeyGenerator',
    'can_translate',
    'increment_usage',
    'show_usage_status',
    'show_limit_reached',
    'get_remaining_translations'
]
