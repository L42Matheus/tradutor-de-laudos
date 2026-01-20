"""
Utilitario para leitura de arquivos
Suporta PDF, imagens e texto
"""

import base64
from io import BytesIO
from typing import Dict, Tuple, Optional

from PyPDF2 import PdfReader

from src.config import IMAGE_MIME_TYPES


def read_text_file(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Le arquivo de texto (.txt)

    Args:
        uploaded_file: Arquivo do Streamlit file_uploader

    Returns:
        tuple: (conteudo, erro)
    """
    try:
        content = uploaded_file.read().decode('utf-8')
        return content, None
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read().decode('latin-1')
            return content, None
        except Exception as e:
            return None, f"Erro ao ler arquivo de texto: {str(e)}"


def read_pdf_file(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Le arquivo PDF e extrai texto

    Args:
        uploaded_file: Arquivo do Streamlit file_uploader

    Returns:
        tuple: (texto_extraido, erro)
    """
    try:
        pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
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


def read_image_file(uploaded_file) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Le arquivo de imagem e retorna em base64

    Args:
        uploaded_file: Arquivo do Streamlit file_uploader

    Returns:
        tuple: (base64_data, media_type, erro)
    """
    try:
        file_type = uploaded_file.type
        media_type = IMAGE_MIME_TYPES.get(file_type)

        if not media_type:
            return None, None, f"Tipo de imagem nao suportado: {file_type}"

        image_data = uploaded_file.read()
        base64_data = base64.standard_b64encode(image_data).decode('utf-8')

        return base64_data, media_type, None

    except Exception as e:
        return None, None, f"Erro ao processar imagem: {str(e)}"


def process_uploaded_file(uploaded_file) -> Dict:
    """
    Processa arquivo enviado e retorna conteudo apropriado

    Args:
        uploaded_file: Arquivo do Streamlit file_uploader

    Returns:
        dict: {
            'type': 'text' ou 'image',
            'content': texto ou dados da imagem,
            'media_type': tipo MIME (apenas para imagens),
            'error': mensagem de erro ou None
        }
    """
    if uploaded_file is None:
        return {
            'type': None,
            'content': None,
            'media_type': None,
            'error': 'Nenhum arquivo enviado'
        }

    file_type = uploaded_file.type
    file_name = uploaded_file.name.lower()

    # Arquivo de texto
    if file_type == 'text/plain' or file_name.endswith('.txt'):
        content, error = read_text_file(uploaded_file)
        return {
            'type': 'text',
            'content': content,
            'media_type': None,
            'error': error
        }

    # Arquivo PDF
    elif file_type == 'application/pdf' or file_name.endswith('.pdf'):
        content, error = read_pdf_file(uploaded_file)
        return {
            'type': 'text',
            'content': content,
            'media_type': None,
            'error': error
        }

    # Arquivo de imagem
    elif file_type.startswith('image/'):
        base64_data, media_type, error = read_image_file(uploaded_file)
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
            'error': f'Tipo de arquivo nao suportado: {file_type}'
        }
