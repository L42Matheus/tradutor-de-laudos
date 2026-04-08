"""
Enums para categorias e tipos de documentos
"""
from enum import Enum


class DocumentCategory(str, Enum):
    """Categorias de documentos médicos"""
    LAUDO = "laudo"
    RECEITA = "receita"
    SAUDE_MENTAL = "saude_mental"


class LaudoType(str, Enum):
    """Tipos de laudos/exames"""
    EXAME_SANGUE = "exame_sangue"
    EXAME_IMAGEM = "exame_imagem"
    EXAME_URINA = "exame_urina"
    BIOPSIA = "biopsia"
    OUTROS = "outros"


class ReceitaType(str, Enum):
    """Tipos de receitas médicas"""
    SIMPLES = "simples"
    CONTROLADA = "controlada"
    ANTIBIOTICO = "antibiotico"


class SaudeMentalType(str, Enum):
    """Tipos de documentos de saúde mental"""
    ANTIDEPRESSIVO = "antidepressivo"
    ANSIOLITICO = "ansiolitico"
    LAUDO_PSIQUIATRICO = "laudo_psiquiatrico"
    OUTROS = "outros"


# Mapeamento de categorias para tipos
CATEGORY_TYPES = {
    DocumentCategory.LAUDO: LaudoType,
    DocumentCategory.RECEITA: ReceitaType,
    DocumentCategory.SAUDE_MENTAL: SaudeMentalType,
}

# Labels em português para o frontend
CATEGORY_LABELS = {
    DocumentCategory.LAUDO: "Laudo/Exame",
    DocumentCategory.RECEITA: "Receita Médica",
    DocumentCategory.SAUDE_MENTAL: "Saúde Mental",
}

LAUDO_TYPE_LABELS = {
    LaudoType.EXAME_SANGUE: "Exame de Sangue",
    LaudoType.EXAME_IMAGEM: "Exame de Imagem (Raio-X, Tomografia, etc)",
    LaudoType.EXAME_URINA: "Exame de Urina",
    LaudoType.BIOPSIA: "Biópsia/Anatomopatológico",
    LaudoType.OUTROS: "Outro tipo de laudo",
}

RECEITA_TYPE_LABELS = {
    ReceitaType.SIMPLES: "Receita Simples",
    ReceitaType.CONTROLADA: "Receita Controlada",
    ReceitaType.ANTIBIOTICO: "Receita de Antibiótico",
}

SAUDE_MENTAL_TYPE_LABELS = {
    SaudeMentalType.ANTIDEPRESSIVO: "Receita de Antidepressivo",
    SaudeMentalType.ANSIOLITICO: "Receita de Ansiolítico",
    SaudeMentalType.LAUDO_PSIQUIATRICO: "Laudo Psiquiátrico",
    SaudeMentalType.OUTROS: "Outro documento de saúde mental",
}


class LLMProvider(str, Enum):
    """Provedores de LLM disponíveis"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"


LLM_PROVIDER_LABELS = {
    LLMProvider.CLAUDE: "Claude (Anthropic)",
    LLMProvider.OPENAI: "GPT (OpenAI)",
    LLMProvider.GEMINI: "Gemini (Google)",
}

LLM_PROVIDER_DESCRIPTIONS = {
    LLMProvider.CLAUDE: "Modelo da Anthropic, excelente para análise médica detalhada",
    LLMProvider.OPENAI: "Modelo da OpenAI, versátil e amplamente testado",
    LLMProvider.GEMINI: "Modelo do Google, com grande contexto e multimodal",
}
