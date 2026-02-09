"""
Rotas de tradução de documentos médicos
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.enums import DocumentCategory
from app.models.requests import TranslateTextRequest
from app.models.responses import TranslateResponse, TranslationResult
from app.services.translator import MedicalTranslator
from app.services.anonymizer import anonymize_text
from app.services.file_processor import process_uploaded_file
from app.config import get_settings

router = APIRouter()


@router.post("/text", response_model=TranslateResponse)
async def translate_text(request: TranslateTextRequest) -> TranslateResponse:
    """
    Traduz texto de documento médico para linguagem acessível.

    - **text**: Texto do documento médico
    - **category**: Categoria (laudo, receita, saude_mental)
    - **document_type**: Tipo específico do documento
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return TranslateResponse(
            success=False,
            data=None,
            error="API key não configurada",
            anonymized_fields=[]
        )

    try:
        # Anonimizar dados pessoais
        anonymized_text, anonymized_fields = anonymize_text(request.text)

        # Traduzir documento
        translator = MedicalTranslator()
        result = translator.translate_text(
            text=anonymized_text,
            tipo=request.document_type,
            categoria=request.category
        )

        return TranslateResponse(
            success=True,
            data=TranslationResult(
                resumo=result.get('resumo', ''),
                detalhado=result.get('detalhado', ''),
                entenda_facil=result.get('entenda_facil', ''),
                glossario=result.get('glossario', {}),
                alertas=result.get('alertas', []),
                is_saude_mental=result.get('is_saude_mental', False) or request.category == DocumentCategory.SAUDE_MENTAL
            ),
            anonymized_fields=anonymized_fields
        )

    except Exception as e:
        return TranslateResponse(
            success=False,
            data=None,
            error=str(e),
            anonymized_fields=[]
        )


@router.post("/file", response_model=TranslateResponse)
async def translate_file(
    file: UploadFile = File(..., description="Arquivo do documento (PDF ou imagem)"),
    category: DocumentCategory = Form(..., description="Categoria do documento"),
    document_type: str = Form(..., description="Tipo específico do documento")
) -> TranslateResponse:
    """
    Traduz arquivo de documento médico (PDF ou imagem) para linguagem acessível.

    - **file**: Arquivo PDF ou imagem (png, jpg, jpeg, gif, webp)
    - **category**: Categoria (laudo, receita, saude_mental)
    - **document_type**: Tipo específico do documento
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return TranslateResponse(
            success=False,
            data=None,
            error="API key não configurada",
            anonymized_fields=[]
        )

    try:
        # Processar arquivo
        file_data = await process_uploaded_file(file)

        if file_data['error']:
            return TranslateResponse(
                success=False,
                data=None,
                error=file_data['error'],
                anonymized_fields=[]
            )

        translator = MedicalTranslator()
        anonymized_fields = []

        if file_data['type'] == 'text':
            # Anonimizar texto extraído
            anonymized_text, anonymized_fields = anonymize_text(file_data['content'])

            # Traduzir texto
            result = translator.translate_text(
                text=anonymized_text,
                tipo=document_type,
                categoria=category
            )
        elif file_data['type'] == 'image':
            # Traduzir imagem diretamente
            result = translator.translate_image(
                image_base64=file_data['content'],
                media_type=file_data['media_type'],
                tipo=document_type,
                categoria=category
            )
        else:
            return TranslateResponse(
                success=False,
                data=None,
                error="Tipo de arquivo não suportado",
                anonymized_fields=[]
            )

        return TranslateResponse(
            success=True,
            data=TranslationResult(
                resumo=result.get('resumo', ''),
                detalhado=result.get('detalhado', ''),
                entenda_facil=result.get('entenda_facil', ''),
                glossario=result.get('glossario', {}),
                alertas=result.get('alertas', []),
                is_saude_mental=result.get('is_saude_mental', False) or category == DocumentCategory.SAUDE_MENTAL
            ),
            anonymized_fields=anonymized_fields
        )

    except Exception as e:
        return TranslateResponse(
            success=False,
            data=None,
            error=str(e),
            anonymized_fields=[]
        )
