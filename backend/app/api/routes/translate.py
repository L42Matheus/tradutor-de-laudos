"""
Rotas de tradução de documentos médicos
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.models.enums import DocumentCategory
from app.models.requests import TranslateTextRequest
from app.models.responses import TranslateResponse, TranslationResult

router = APIRouter()


@router.post("/text", response_model=TranslateResponse)
async def translate_text(request: TranslateTextRequest) -> TranslateResponse:
    """
    Traduz texto de documento médico para linguagem acessível.

    - **text**: Texto do documento médico
    - **category**: Categoria (laudo, receita, saude_mental)
    - **document_type**: Tipo específico do documento
    """
    # TODO: Implementar na Fase 2
    return TranslateResponse(
        success=True,
        data=TranslationResult(
            resumo="[Implementação pendente]",
            detalhado="[Implementação pendente]",
            entenda_facil="[Implementação pendente]",
            glossario={},
            alertas=[],
            is_saude_mental=request.category == DocumentCategory.SAUDE_MENTAL
        ),
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
    # TODO: Implementar na Fase 2
    return TranslateResponse(
        success=True,
        data=TranslationResult(
            resumo="[Implementação pendente - upload de arquivo]",
            detalhado="[Implementação pendente]",
            entenda_facil="[Implementação pendente]",
            glossario={},
            alertas=[],
            is_saude_mental=category == DocumentCategory.SAUDE_MENTAL
        ),
        anonymized_fields=[]
    )
