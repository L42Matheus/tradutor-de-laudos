"""
Modulo de interface do usuario
"""

from .components import (
    show_header,
    show_terms,
    show_footer,
    show_category_selector,
    show_type_selector,
    show_input_method,
    show_file_uploader,
    show_text_input,
    show_results,
    show_theme_toggle,
    apply_custom_styles
)
from .apoio_emocional import show_apoio_emocional

__all__ = [
    'show_header',
    'show_terms',
    'show_footer',
    'show_category_selector',
    'show_type_selector',
    'show_input_method',
    'show_file_uploader',
    'show_text_input',
    'show_results',
    'show_theme_toggle',
    'apply_custom_styles',
    'show_apoio_emocional'
]
