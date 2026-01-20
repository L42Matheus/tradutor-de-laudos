import re

def anonymize_text(text):
    """
    Remove dados pessoais sensíveis do texto do laudo
    
    Args:
        text: Texto original do laudo
        
    Returns:
        tuple: (texto_anonimizado, lista_de_dados_removidos)
    """
    
    anonimizado = text
    dados_removidos = []
    
    # 1. Remover CPF (formato: 000.000.000-00 ou 00000000000)
    cpf_pattern = r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}'
    if re.search(cpf_pattern, anonimizado):
        anonimizado = re.sub(cpf_pattern, '[CPF REMOVIDO]', anonimizado)
        dados_removidos.append('CPF')
    
    # 2. Remover RG (formato variável, mas geralmente 0.000.000 ou similar)
    rg_pattern = r'RG:?\s*\d{1,2}\.?\d{3}\.?\d{3}-?[0-9xX]?'
    if re.search(rg_pattern, anonimizado, re.IGNORECASE):
        anonimizado = re.sub(rg_pattern, '[RG REMOVIDO]', anonimizado, flags=re.IGNORECASE)
        dados_removidos.append('RG')
    
    # 3. Remover datas de nascimento (formato: dd/mm/aaaa)
    # Apenas datas que parecem ser nascimentos (anos < 2010)
    data_nasc_pattern = r'\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(19\d{2}|200\d)\b'
    if re.search(data_nasc_pattern, anonimizado):
        anonimizado = re.sub(data_nasc_pattern, '[DATA REMOVIDA]', anonimizado)
        dados_removidos.append('Data de Nascimento')
    
    # 4. Remover endereços completos (simplificado)
    # Procura por padrões como "Rua/Av ... número ... CEP"
    endereco_pattern = r'(Rua|Avenida|Av\.|R\.|Travessa)[^,\n]{10,80}CEP:?\s*\d{5}-?\d{3}'
    if re.search(endereco_pattern, anonimizado, re.IGNORECASE):
        anonimizado = re.sub(endereco_pattern, '[ENDEREÇO REMOVIDO]', anonimizado, flags=re.IGNORECASE)
        dados_removidos.append('Endereço')
    
    # 5. Remover telefones (formato: (00) 00000-0000 ou variações)
    telefone_pattern = r'\(?\d{2}\)?\s*9?\d{4}-?\d{4}'
    if re.search(telefone_pattern, anonimizado):
        anonimizado = re.sub(telefone_pattern, '[TELEFONE REMOVIDO]', anonimizado)
        dados_removidos.append('Telefone')
    
    # 6. Remover emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(email_pattern, anonimizado):
        anonimizado = re.sub(email_pattern, '[EMAIL REMOVIDO]', anonimizado)
        dados_removidos.append('Email')
    
    # 7. Remover nomes próprios comuns em laudos
    # Padrões como "Paciente: Nome Completo" ou "Nome: Nome Completo"
    nome_patterns = [
        r'Paciente:?\s+([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+\s+){1,4}[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+',
        r'Nome:?\s+([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+\s+){1,4}[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+',
    ]
    
    for pattern in nome_patterns:
        if re.search(pattern, anonimizado):
            anonimizado = re.sub(pattern, lambda m: m.group().split(':')[0] + ': [NOME REMOVIDO]', anonimizado)
            if 'Nome' not in dados_removidos:
                dados_removidos.append('Nome')
    
    # 8. Remover cartão SUS/CNS
    cns_pattern = r'\b\d{3}\s?\d{4}\s?\d{4}\s?\d{4}\b'
    if re.search(cns_pattern, anonimizado):
        anonimizado = re.sub(cns_pattern, '[CNS REMOVIDO]', anonimizado)
        dados_removidos.append('CNS/Cartão SUS')
    
    return anonimizado, list(set(dados_removidos))


def test_anonymizer():
    """
    Função de teste para validar a anonimização
    """
    texto_teste = """
    Paciente: João da Silva Santos
    CPF: 123.456.789-00
    Data Nascimento: 15/03/1985
    Telefone: (11) 98765-4321
    Email: joao.silva@email.com
    
    Resultado do Hemograma:
    - Hemoglobina: 14.5 g/dL
    - Leucócitos: 7.200/mm³
    """
    
    resultado, removidos = anonymize_text(texto_teste)
    print("TEXTO ANONIMIZADO:")
    print(resultado)
    print("\nDADOS REMOVIDOS:", removidos)


if __name__ == "__main__":
    test_anonymizer()
