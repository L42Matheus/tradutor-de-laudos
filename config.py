"""
Configuracoes e constantes do sistema
"""

# Categorias de documentos aceitos
class DocumentCategory:
    LAUDO = "laudo"
    RECEITA = "receita"


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
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Configuracoes de requisicao
MAX_TOKENS = 4000
TEMPERATURE = 0.3
