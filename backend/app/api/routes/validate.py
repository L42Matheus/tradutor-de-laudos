"""
Rotas de validação de documentos médicos
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.requests import ValidateTextRequest
from app.models.responses import ValidateResponse, ValidationResult

router = APIRouter()


@router.post("/text", response_model=ValidateResponse)
async def validate_text(request: ValidateTextRequest) -> ValidateResponse:
    """
    Valida se o texto é um documento médico válido.

    - **text**: Texto para validar
    """
    # TODO: Implementar na Fase 2
    return ValidateResponse(
        success=True,
        data=ValidationResult(
            is_valid=True,
            document_type="laudo",
            suggested_category=None,
            message="[Validação pendente de implementação]"
        )
    )


@router.post("/file", response_model=ValidateResponse)
async def validate_file(
    file: UploadFile = File(..., description="Arquivo para validar")
) -> ValidateResponse:
    """
    Valida se o arquivo é um documento médico válido.

    - **file**: Arquivo PDF ou imagem
    """
    # TODO: Implementar na Fase 2
    return ValidateResponse(
        success=True,
        data=ValidationResult(
            is_valid=True,
            document_type="laudo",
            suggested_category=None,
            message="[Validação de arquivo pendente de implementação]"
        )
    )
