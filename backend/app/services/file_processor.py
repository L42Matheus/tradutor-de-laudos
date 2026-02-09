"""
Utilitario para processamento de arquivos enviados via API
Suporta PDF, imagens e texto
"""

import base64
from io import BytesIO
from typing import Dict, Optional

from fastapi import UploadFile
from PyPDF2 import PdfReader


# Tipos MIME suportados
IMAGE_MIME_TYPES = {
    'image/png': 'image/png',
    'image/jpeg': 'image/jpeg',
    'image/jpg': 'image/jpeg',
    'image/gif': 'image/gif',
    'image/webp': 'image/webp'
}


async def read_text_file(file: UploadFile) -> tuple[Optional[str], Optional[str]]:
    """
    Le arquivo de texto (.txt)

    Args:
        file: Arquivo UploadFile do FastAPI

    Returns:
        tuple: (conteudo, erro)
    """
    try:
        content = await file.read()
        try:
            return content.decode('utf-8'), None
        except UnicodeDecodeError:
            return content.decode('latin-1'), None
    except Exception as e:
        return None, f"Erro ao ler arquivo de texto: {str(e)}"


async def read_pdf_file(file: UploadFile) -> tuple[Optional[str], Optional[str]]:
    """
    Le arquivo PDF e extrai texto

    Args:
        file: Arquivo UploadFile do FastAPI

    Returns:
        tuple: (texto_extraido, erro)
    """
    try:
        content = await file.read()
        pdf_reader = PdfReader(BytesIO(content))
        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            return None, "PDF nao contem texto extraivel. Pode ser um PDF escaneado. Tente enviar como imagem."

        return text, None

    except Exception as e:
        return None, f"Erro ao ler PDF: {str(e)}"


async def read_image_file(file: UploadFile) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Le arquivo de imagem e retorna em base64

    Args:
        file: Arquivo UploadFile do FastAPI

    Returns:
        tuple: (base64_data, media_type, erro)
    """
    try:
        content_type = file.content_type or ''
        media_type = IMAGE_MIME_TYPES.get(content_type)

        if not media_type:
            # Tentar detectar pelo nome do arquivo
            filename = file.filename or ''
            ext = filename.lower().split('.')[-1] if '.' in filename else ''
            ext_to_mime = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            media_type = ext_to_mime.get(ext)

        if not media_type:
            return None, None, f"Tipo de imagem nao suportado: {content_type}"

        image_data = await file.read()
        base64_data = base64.standard_b64encode(image_data).decode('utf-8')

        return base64_data, media_type, None

    except Exception as e:
        return None, None, f"Erro ao processar imagem: {str(e)}"


async def process_uploaded_file(file: UploadFile) -> Dict:
    """
    Processa arquivo enviado e retorna conteudo apropriado

    Args:
        file: Arquivo UploadFile do FastAPI

    Returns:
        dict: {
            'type': 'text' ou 'image',
            'content': texto ou dados da imagem,
            'media_type': tipo MIME (apenas para imagens),
            'error': mensagem de erro ou None
        }
    """
    if file is None:
        return {
            'type': None,
            'content': None,
            'media_type': None,
            'error': 'Nenhum arquivo enviado'
        }

    content_type = file.content_type or ''
    file_name = (file.filename or '').lower()

    # Arquivo de texto
    if content_type == 'text/plain' or file_name.endswith('.txt'):
        content, error = await read_text_file(file)
        return {
            'type': 'text',
            'content': content,
            'media_type': None,
            'error': error
        }

    # Arquivo PDF
    elif content_type == 'application/pdf' or file_name.endswith('.pdf'):
        content, error = await read_pdf_file(file)
        return {
            'type': 'text',
            'content': content,
            'media_type': None,
            'error': error
        }

    # Arquivo de imagem
    elif content_type.startswith('image/') or any(file_name.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
        base64_data, media_type, error = await read_image_file(file)
        return {
            'type': 'image',
            'content': base64_data,
            'media_type': media_type,
            'error': error
        }

    else:
        return {
            'type': None,
            'content': None,
            'media_type': None,
            'error': f'Tipo de arquivo nao suportado: {content_type}'
        }
