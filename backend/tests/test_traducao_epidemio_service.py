from app.services.traducao_epidemio_service import (
    _adicionar_alertas_criticos,
    _validar_estrutura,
)


def test_validar_estrutura_preserva_blocos_distintos():
    resultado = _validar_estrutura(
        {
            "resumo": (
                "Resumo claro com explicacao suficiente para o paciente entender o achado principal, "
                "a regiao afetada e o impacto funcional observado no exame."
            ),
            "detalhado": "Explicacao detalhada",
            "entenda_facil": "Imagine como um cano entupido",
            "texto_traduzido": "Texto traduzido completo",
            "glossario": {"edema": "inchaco"},
            "alertas": ["Procure atendimento"],
            "condicao_categoria": "neurologico",
            "faixa_etaria": "31-45",
        }
    )

    assert resultado["resumo"].startswith("Resumo claro com explicacao suficiente")
    assert resultado["detalhado"] == "Explicacao detalhada"
    assert resultado["entenda_facil"] == "Imagine como um cano entupido"
    assert resultado["texto_traduzido"] == "Texto traduzido completo"
    assert resultado["alertas"] == ["Procure atendimento"]


def test_validar_estrutura_preenche_fallbacks_sem_colapsar_alertas():
    resultado = _validar_estrutura(
        {
            "texto_traduzido": "Texto principal",
            "alertas": "Alerta unico",
            "condicao_categoria": "invalido",
            "faixa_etaria": "invalida",
        }
    )

    assert resultado["resumo"] == "Texto principal"
    assert resultado["detalhado"] == "Texto principal"
    assert resultado["entenda_facil"] == "Texto principal"
    assert resultado["alertas"] == ["Alerta unico"]
    assert resultado["condicao_categoria"] == "outro"
    assert resultado["faixa_etaria"] == "nao_informado"


def test_validar_estrutura_expande_resumo_quando_vier_curto_demais():
    resultado = _validar_estrutura(
        {
            "resumo": "Visao reduzida no olho direito.",
            "detalhado": (
                "O exame oftalmologico mostra visao normal no olho esquerdo com pequena correcao para "
                "miopia. No olho direito, a visao esta muito reduzida, com capacidade apenas de contar "
                "dedos a 2 metros, caracterizando cegueira unilateral e impacto funcional importante."
            ),
            "entenda_facil": "E como se um olho enxergasse bem e o outro estivesse quase apagado.",
            "texto_traduzido": (
                "O exame mostra que o olho esquerdo enxerga normalmente, enquanto o olho direito tem uma "
                "perda muito importante da visao, suficiente para limitar bastante o que a pessoa consegue ver."
            ),
        }
    )

    assert len(resultado["resumo"]) >= 120
    assert resultado["resumo"] != "Visao reduzida no olho direito."


def test_adiciona_alerta_urgente_para_lesao_expansiva_cerebral():
    resultado = _adicionar_alertas_criticos(
        (
            "Lesao expansiva frontoparietal direita com edema perilesional, compressao do ventriculo "
            "lateral direito e desvio das estruturas da linha media."
        ),
        {
            "alertas": ["Necessario acompanhamento especializado para definir a natureza da lesao."]
        },
    )

    texto_alertas = " ".join(resultado["alertas"]).lower()
    assert "urgente" in texto_alertas
    assert "neurolog" in texto_alertas or "neurocir" in texto_alertas
