"""
Prompts especificos para receitas medicas
"""

from .base import PROMPT_BASE_RECEITA


PROMPT_RECEITA_SIMPLES = PROMPT_BASE_RECEITA + """

ESPECIALIZACAO EM RECEITAS SIMPLES:
- Explique cada medicamento prescrito
- Detalhe: nome comercial e generico (se disponivel)
- Explique a dosagem de forma clara (ex: "1 comprimido de manha e 1 a noite")
- Informe duracao do tratamento
- Liste efeitos colaterais mais comuns
- Alerte sobre restricoes (alcool, dirigir, etc)
"""

PROMPT_RECEITA_CONTROLADA = PROMPT_BASE_RECEITA + """

ESPECIALIZACAO EM RECEITAS DE CONTROLE ESPECIAL:
- Explique que sao medicamentos controlados e por que
- Detalhe a importancia de seguir a dosagem exata
- Alerte sobre riscos de dependencia quando aplicavel
- Explique que a receita tem validade e controle
- Destaque que NAO deve ser compartilhado com outras pessoas
- Informe sobre possiveis efeitos de abstinencia
"""

PROMPT_RECEITA_ANTIBIOTICO = PROMPT_BASE_RECEITA + """

ESPECIALIZACAO EM RECEITAS DE ANTIBIOTICO:
- Explique a importancia de completar todo o tratamento
- Alerte que NAO deve parar antes do prazo mesmo se melhorar
- Explique horarios ideais para tomar
- Informe sobre interacoes com alimentos
- Alerte sobre efeitos no intestino (diarreia, etc)
- Explique riscos de resistencia bacteriana se nao completar
"""
