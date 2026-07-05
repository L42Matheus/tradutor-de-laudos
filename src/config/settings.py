"""
Configuracoes e constantes do sistema
"""


class DocumentCategory:
    """Categorias de documentos aceitos"""
    LAUDO = "laudo"
    RECEITA = "receita"
    SAUDE_MENTAL = "saude_mental"


# Tipos de laudos medicos
TIPOS_LAUDO = [
    "Exame de Sangue",
    "Exame de Imagem (RX, TC, RM)",
    "Exame de Urina",
    "Biopsia/Patologia",
    "Outro"
]

# Tipos de receitas medicas
TIPOS_RECEITA = [
    "Receita Simples",
    "Receita de Controle Especial",
    "Receita de Antibiotico"
]

# Tipos de documentos de saude mental
TIPOS_SAUDE_MENTAL = [
    "Receita de Antidepressivo",
    "Receita de Ansiolitico",
    "Laudo Psiquiatrico",
    "Outro"
]

# Formatos de arquivo aceitos
ALLOWED_FILE_TYPES = ['pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'webp']

# Tipos MIME para imagens
IMAGE_MIME_TYPES = {
    'image/jpeg': 'image/jpeg',
    'image/jpg': 'image/jpeg',
    'image/png': 'image/png',
    'image/gif': 'image/gif',
    'image/webp': 'image/webp'
}

# Modelo Claude utilizado
CLAUDE_MODEL = "claude-sonnet-4-5"

# Configuracoes de requisicao
MAX_TOKENS = 4000
TEMPERATURE = 0.3

# Configuracoes de cache
CACHE_ENABLED = True
CACHE_TTL_SECONDS = 3600  # 1 hora
CACHE_MAX_SIZE = 100  # Maximo de entradas em memoria

# Limites de uso
MAX_TEXT_LENGTH = 10000
MAX_REQUESTS_PER_SESSION = 20
FREE_TRANSLATIONS_LIMIT = 3
