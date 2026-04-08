"""
Rotas de traducao de documentos medicos
"""
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends

from app.config import get_settings
from app.database import get_db
from app.models.db_models import User
from app.models.enums import DocumentCategory
from app.models.requests import TranslateTextRequest
from app.models.responses import TranslateResponse, TranslationResult
from app.services.anonymizer import anonymize_text
from app.services.auth_service import get_current_user_optional
from app.services.authorship_detector import ProfessionalAuthorshipDetector
from app.services.file_processor import process_uploaded_file
from app.services.history_service import generate_file_hash, register_translation_history
from app.services.translator import MedicalTranslator
from app.services.validator import DocumentValidator
from sqlalchemy.orm import Session

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


def _detect_authorship_for_file(detector: ProfessionalAuthorshipDetector, file_data: dict) -> dict:
    """Detecta indicios de autoria profissional no arquivo processado."""
    if file_data["type"] == "text":
        return detector.detect_from_text(file_data["content"])
    if file_data["type"] == "image":
        return detector.detect_from_image(
            image_base64=file_data["content"],
            media_type=file_data["media_type"],
        )
    return {
        "professional_authorship_detected": False,
        "professional_authorship_evidence": [],
    }


@router.post("/text", response_model=TranslateResponse)
async def translate_text(
    request: TranslateTextRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> TranslateResponse:
    """
    Traduz texto de documento medico para linguagem acessivel.
    """
    # Escolher provider: Request > Preferência do Usuário > Default (Claude)
    provider = request.provider
    if not provider and current_user:
        provider = current_user.preferred_llm_provider

    try:
        validator = DocumentValidator()
        detector = ProfessionalAuthorshipDetector()
        validation = validator.validate_text(request.text)
        if not validation.get("is_valid"):
            return _build_validation_error(
                validation.get("message", "Documento fora do escopo medico")
            )

        authorship = detector.detect_from_text(request.text)
        anonymized_text, anonymized_fields = anonymize_text(request.text)

        translator = MedicalTranslator(provider_name=provider)
        result = translator.translate_text(
            text=anonymized_text,
            tipo=request.document_type,
            categoria=request.category
        )

        register_translation_history(
            db=db,
            user=current_user,
            source=f"translate_text_{provider or 'claude'}",
            input_type="text",
            document_category=request.category,
            document_type=request.document_type,
            original_text=anonymized_text,
            result_payload=result,
        )
        db.commit()

        return TranslateResponse(
            success=True,
            data=TranslationResult(
                resumo=result.get("resumo", ""),
                detalhado=result.get("detalhado", ""),
                entenda_facil=result.get("entenda_facil", ""),
                glossario=result.get("glossario", {}),
                alertas=result.get("alertas", []),
                is_saude_mental=result.get("is_saude_mental", False)
                or request.category == DocumentCategory.SAUDE_MENTAL,
                from_cache=result.get("from_cache", False),
                professional_authorship_detected=authorship["professional_authorship_detected"],
                professional_authorship_evidence=authorship["professional_authorship_evidence"],
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
    document_type: str = Form(..., description="Tipo especifico do documento"),
    provider: Optional[str] = Form(None, description="Provedor de LLM (claude, openai, gemini)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> TranslateResponse:
    """
    Traduz arquivo de documento medico (PDF ou imagem) para linguagem acessivel.
    """
    settings = get_settings()
    
    # Escolher provider: Form > Preferência do Usuário > Default (Claude)
    selected_provider = provider
    if not selected_provider and current_user:
        selected_provider = current_user.preferred_llm_provider

    try:
        # Validar tamanho do arquivo antes de processar
        file_bytes = await file.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        if file_size_mb > settings.max_file_size_mb:
            return TranslateResponse(
                success=False,
                data=None,
                error=f"Arquivo muito grande ({file_size_mb:.1f}MB). O limite é {settings.max_file_size_mb}MB.",
                anonymized_fields=[]
            )

        await file.seek(0)
        file_data = await process_uploaded_file(file)

        if file_data["error"]:
            return TranslateResponse(
                success=False,
                data=None,
                error=file_data["error"],
                anonymized_fields=[]
            )

        validator = DocumentValidator()
        detector = ProfessionalAuthorshipDetector()
        validation = _validate_processed_file(validator, file_data)
        if not validation.get("is_valid"):
            return _build_validation_error(
                validation.get("message", "Documento fora do escopo medico")
            )

        translator = MedicalTranslator(provider_name=selected_provider)
        authorship = _detect_authorship_for_file(detector, file_data)
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

        register_translation_history(
            db=db,
            user=current_user,
            source=f"translate_file_{selected_provider or 'claude'}",
            input_type=file_data["type"],
            document_category=category,
            document_type=document_type,
            original_text=anonymized_text if file_data["type"] == "text" else None,
            original_image_base64=file_data["content"] if file_data["type"] == "image" else None,
            original_image_media_type=file_data["media_type"] if file_data["type"] == "image" else None,
            result_payload=result,
            file_hash=generate_file_hash(file_bytes),
        )
        db.commit()

        return TranslateResponse(
            success=True,
            data=TranslationResult(
                resumo=result.get("resumo", ""),
                detalhado=result.get("detalhado", ""),
                entenda_facil=result.get("entenda_facil", ""),
                glossario=result.get("glossario", {}),
                alertas=result.get("alertas", []),
                is_saude_mental=result.get("is_saude_mental", False)
                or category == DocumentCategory.SAUDE_MENTAL,
                from_cache=result.get("from_cache", False),
                professional_authorship_detected=authorship["professional_authorship_detected"],
                professional_authorship_evidence=authorship["professional_authorship_evidence"],
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
