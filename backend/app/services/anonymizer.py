"""
Servico de anonimizacao de dados pessoais
Remove informacoes sensiveis de documentos (LGPD)
"""

import re
from typing import Tuple, List


def anonymize_text(text: str) -> Tuple[str, List[str]]:
    """
    Remove dados pessoais sensiveis do texto do documento

    Args:
        text: Texto original do documento

    Returns:
        tuple: (texto_anonimizado, lista_de_dados_removidos)
    """
    anonimizado = text
    dados_removidos = []

    # Padroes de dados sensiveis
    patterns = {
        'CPF': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
        'RG': r'RG:?\s*\d{1,2}\.?\d{3}\.?\d{3}-?[0-9xX]?',
        'Data de Nascimento': r'\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(19\d{2}|200\d)\b',
        'Endereco': r'(Rua|Avenida|Av\.|R\.|Travessa)[^,\n]{10,80}CEP:?\s*\d{5}-?\d{3}',
        'Telefone': r'\(?\d{2}\)?\s*9?\d{4}-?\d{4}',
        'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'CNS/Cartao SUS': r'\b\d{3}\s?\d{4}\s?\d{4}\s?\d{4}\b'
    }

    # Aplicar cada padrao
    for tipo, pattern in patterns.items():
        flags = re.IGNORECASE if tipo in ['RG', 'Endereco'] else 0
        if re.search(pattern, anonimizado, flags):
            anonimizado = re.sub(pattern, f'[{tipo.upper()} REMOVIDO]', anonimizado, flags=flags)
            dados_removidos.append(tipo)

    # Padroes especiais para nomes
    nome_patterns = [
        r'Paciente:?\s+([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+\s+){1,4}[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+',
        r'Nome:?\s+([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+\s+){1,4}[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+',
    ]

    for pattern in nome_patterns:
        if re.search(pattern, anonimizado):
            anonimizado = re.sub(
                pattern,
                lambda m: m.group().split(':')[0] + ': [NOME REMOVIDO]',
                anonimizado
            )
            if 'Nome' not in dados_removidos:
                dados_removidos.append('Nome')

    return anonimizado, list(set(dados_removidos))
