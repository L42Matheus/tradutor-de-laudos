"""
Rotas de traducao de documentos medicos
"""
from fastapi import APIRouter, UploadFile, File, Form

from app.config import get_settings
from app.models.enums import DocumentCategory
from app.models.requests import TranslateTextRequest
from app.models.responses import TranslateResponse, TranslationResult
from app.services.anonymizer import anonymize_text
from app.services.file_processor import process_uploaded_file
from app.services.translator import MedicalTranslator
from app.services.validator import DocumentValidator

router = APIRouter()


def _build_validation_error(message: str) -> TranslateResponse:
    """Retorna resposta padronizada quando o documento nao e aceito."""
    return TranslateResponse(
        success=False,
        data=None,
        error=f"Documento nao aceito: {message}",
        anonymized_fields=[]
    )


def _validate_processed_file(validator: DocumentValidator, file_data: dict) -> dict:
    """Valida o arquivo ja processado antes de traduzir."""
    if file_data["type"] == "text":
        return validator.validate_text(file_data["content"])
    if file_data["type"] == "image":
        return validator.validate_image(
            image_base64=file_data["content"],
            media_type=file_data["media_type"],
        )
    return {
        "is_valid": False,
        "document_type": None,
        "message": "Tipo de arquivo nao suportado",
    }


@router.post("/text", response_model=TranslateResponse)
async def translate_text(request: TranslateTextRequest) -> TranslateResponse:
    """
    Traduz texto de documento medico para linguagem acessivel.

    - **text**: Texto do documento medico
    - **category**: Categoria (laudo, receita, saude_mental)
    - **document_type**: Tipo especifico do documento
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return TranslateResponse(
            success=False,
            data=None,
            error="API key nao configurada",
            anonymized_fields=[]
        )

    try:
        validator = DocumentValidator()
        validation = validator.validate_text(request.text)
        if not validation.get("is_valid"):
            return _build_validation_error(
                validation.get("message", "Documento fora do escopo medico")
            )

        anonymized_text, anonymized_fields = anonymize_text(request.text)

        translator = MedicalTranslator()
        result = translator.translate_text(
            text=anonymized_text,
            tipo=request.document_type,
            categoria=request.category
        )

        return TranslateResponse(
            success=True,
            data=TranslationResult(
                resumo=result.get("resumo", ""),
                detalhado=result.get("detalhado", ""),
                entenda_facil=result.get("entenda_facil", ""),
                glossario=result.get("glossario", {}),
                alertas=result.get("alertas", []),
                is_saude_mental=result.get("is_saude_mental", False)
                or request.category == DocumentCategory.SAUDE_MENTAL
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
    document_type: str = Form(..., description="Tipo especifico do documento")
) -> TranslateResponse:
    """
    Traduz arquivo de documento medico (PDF ou imagem) para linguagem acessivel.

    - **file**: Arquivo PDF ou imagem (png, jpg, jpeg, gif, webp)
    - **category**: Categoria (laudo, receita, saude_mental)
    - **document_type**: Tipo especifico do documento
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return TranslateResponse(
            success=False,
            data=None,
            error="API key nao configurada",
            anonymized_fields=[]
        )

    try:
        file_data = await process_uploaded_file(file)

        if file_data["error"]:
            return TranslateResponse(
                success=False,
                data=None,
                error=file_data["error"],
                anonymized_fields=[]
            )

        validator = DocumentValidator()
        validation = _validate_processed_file(validator, file_data)
        if not validation.get("is_valid"):
            return _build_validation_error(
                validation.get("message", "Documento fora do escopo medico")
            )

        translator = MedicalTranslator()
        anonymized_fields = []

        if file_data["type"] == "text":
            anonymized_text, anonymized_fields = anonymize_text(file_data["content"])
            result = translator.translate_text(
                text=anonymized_text,
                tipo=document_type,
                categoria=category
            )
        elif file_data["type"] == "image":
            result = translator.translate_image(
                image_base64=file_data["content"],
                media_type=file_data["media_type"],
                tipo=document_type,
                categoria=category
            )
        else:
            return TranslateResponse(
                success=False,
                data=None,
                error="Tipo de arquivo nao suportado",
                anonymized_fields=[]
            )

        return TranslateResponse(
            success=True,
            data=TranslationResult(
                resumo=result.get("resumo", ""),
                detalhado=result.get("detalhado", ""),
                entenda_facil=result.get("entenda_facil", ""),
                glossario=result.get("glossario", {}),
                alertas=result.get("alertas", []),
                is_saude_mental=result.get("is_saude_mental", False)
                or category == DocumentCategory.SAUDE_MENTAL
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
