"""
Serviço de parsing de entrada - extrai texto de PDF, imagem ou texto puro.
Para imagens, usa Anthropic Vision API para OCR.
"""
import base64
from io import BytesIO
from typing import Optional, Tuple

from fastapi import UploadFile
from PyPDF2 import PdfReader
import anthropic

from app.config import get_settings


settings = get_settings()

IMAGE_MIME_TYPES = {
    'image/png': 'image/png',
    'image/jpeg': 'image/jpeg',
    'image/jpg': 'image/jpeg',
    'image/gif': 'image/gif',
    'image/webp': 'image/webp'
}


async def extrair_texto_pdf(file_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrai texto de um arquivo PDF usando PyPDF2.

    Args:
        file_bytes: Conteúdo do PDF em bytes

    Returns:
        Tuple[texto_extraido, erro]
    """
    try:
        pdf_reader = PdfReader(BytesIO(file_bytes))
        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            return None, "PDF não contém texto extraível. Pode ser um PDF escaneado."

        return text.strip(), None

    except Exception as e:
        return None, f"Erro ao ler PDF: {str(e)}"


async def extrair_texto_imagem(file_bytes: bytes, media_type: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrai texto de uma imagem usando Anthropic Vision API (OCR via LLM).

    Args:
        file_bytes: Conteúdo da imagem em bytes
        media_type: Tipo MIME da imagem (image/png, image/jpeg, etc.)

    Returns:
        Tuple[texto_extraido, erro]
    """
    try:
        base64_data = base64.standard_b64encode(file_bytes).decode('utf-8')

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "Transcreva todo o texto deste laudo médico, preservando a estrutura original. Retorne apenas o texto transcrito, sem comentários adicionais."
                        }
                    ]
                }
            ]
        )

        texto = response.content[0].text

        if not texto.strip():
            return None, "Não foi possível extrair texto da imagem."

        return texto.strip(), None

    except anthropic.APIError as e:
        return None, f"Erro na API Anthropic: {str(e)}"
    except Exception as e:
        return None, f"Erro ao processar imagem: {str(e)}"


def extrair_texto_puro(texto: str) -> Tuple[str, None]:
    """
    Retorna texto puro sem processamento.

    Args:
        texto: Texto de entrada

    Returns:
        Tuple[texto, None]
    """
    return texto.strip(), None


def detectar_tipo_mime(file: UploadFile) -> Optional[str]:
    """
    Detecta o tipo MIME do arquivo.

    Args:
        file: Arquivo UploadFile do FastAPI

    Returns:
        Tipo MIME ou None
    """
    content_type = file.content_type or ''
    filename = (file.filename or '').lower()

    if content_type == 'text/plain' or filename.endswith('.txt'):
        return 'text/plain'

    if content_type == 'application/pdf' or filename.endswith('.pdf'):
        return 'application/pdf'

    if content_type in IMAGE_MIME_TYPES:
        return IMAGE_MIME_TYPES[content_type]

    ext_to_mime = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }

    for ext, mime in ext_to_mime.items():
        if filename.endswith(f'.{ext}'):
            return mime

    return None


async def parse_entrada(
    arquivo: Optional[UploadFile] = None,
    texto: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Função unificada de parsing - detecta o tipo e extrai texto.

    Args:
        arquivo: Arquivo UploadFile (PDF, imagem ou texto)
        texto: Texto puro (se arquivo não fornecido)

    Returns:
        Tuple[texto_extraido, erro]
    """
    if texto and texto.strip():
        return extrair_texto_puro(texto)

    if not arquivo:
        return None, "Nenhuma entrada fornecida (arquivo ou texto)."

    mime_type = detectar_tipo_mime(arquivo)

    if not mime_type:
        return None, f"Tipo de arquivo não suportado: {arquivo.content_type}"

    file_bytes = await arquivo.read()
    await arquivo.seek(0)

    if mime_type == 'text/plain':
        try:
            texto = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            texto = file_bytes.decode('latin-1')
        return extrair_texto_puro(texto)

    if mime_type == 'application/pdf':
        return await extrair_texto_pdf(file_bytes)

    if mime_type.startswith('image/'):
        return await extrair_texto_imagem(file_bytes, mime_type)

    return None, f"Tipo de arquivo não suportado: {mime_type}"
