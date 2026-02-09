"""
Rotas de validação de documentos médicos
"""
from fastapi import APIRouter, UploadFile, File

from app.models.enums import DocumentCategory
from app.models.requests import ValidateTextRequest
from app.models.responses import ValidateResponse, ValidationResult
from app.services.validator import DocumentValidator
from app.services.file_processor import process_uploaded_file
from app.config import get_settings

router = APIRouter()


def _map_document_type_to_category(doc_type: str) -> DocumentCategory:
    """Mapeia o tipo de documento detectado para a categoria"""
    if doc_type == 'saude_mental':
        return DocumentCategory.SAUDE_MENTAL
    elif doc_type == 'receita':
        return DocumentCategory.RECEITA
    elif doc_type == 'laudo':
        return DocumentCategory.LAUDO
    return None


@router.post("/text", response_model=ValidateResponse)
async def validate_text(request: ValidateTextRequest) -> ValidateResponse:
    """
    Valida se o texto é um documento médico válido.

    - **text**: Texto para validar
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return ValidateResponse(
            success=False,
            data=None,
            error="API key não configurada"
        )

    try:
        validator = DocumentValidator()
        result = validator.validate_text(request.text)

        suggested_category = _map_document_type_to_category(result.get('document_type'))

        return ValidateResponse(
            success=True,
            data=ValidationResult(
                is_valid=result.get('is_valid', False),
                document_type=result.get('document_type'),
                suggested_category=suggested_category,
                message=result.get('message', '')
            )
        )

    except Exception as e:
        return ValidateResponse(
            success=False,
            data=None,
            error=str(e)
        )


@router.post("/file", response_model=ValidateResponse)
async def validate_file(
    file: UploadFile = File(..., description="Arquivo para validar")
) -> ValidateResponse:
    """
    Valida se o arquivo é um documento médico válido.

    - **file**: Arquivo PDF ou imagem
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return ValidateResponse(
            success=False,
            data=None,
            error="API key não configurada"
        )

    try:
        # Processar arquivo
        file_data = await process_uploaded_file(file)

        if file_data['error']:
            return ValidateResponse(
                success=False,
                data=None,
                error=file_data['error']
            )

        validator = DocumentValidator()

        if file_data['type'] == 'text':
            result = validator.validate_text(file_data['content'])
        elif file_data['type'] == 'image':
            result = validator.validate_image(
                image_base64=file_data['content'],
                media_type=file_data['media_type']
            )
        else:
            return ValidateResponse(
                success=False,
                data=None,
                error="Tipo de arquivo não suportado"
            )

        suggested_category = _map_document_type_to_category(result.get('document_type'))

        return ValidateResponse(
            success=True,
            data=ValidationResult(
                is_valid=result.get('is_valid', False),
                document_type=result.get('document_type'),
                suggested_category=suggested_category,
                message=result.get('message', '')
            )
        )

    except Exception as e:
        return ValidateResponse(
            success=False,
            data=None,
            error=str(e)
        )
