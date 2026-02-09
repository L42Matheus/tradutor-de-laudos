"""
Modelos de requisição Pydantic
"""
from pydantic import BaseModel, Field
from typing import Optional
from app.models.enums import DocumentCategory


class TranslateTextRequest(BaseModel):
    """Requisição para tradução de texto"""
    text: str = Field(..., min_length=10, max_length=10000, description="Texto do documento médico")
    category: DocumentCategory = Field(..., description="Categoria do documento")
    document_type: str = Field(..., description="Tipo específico do documento")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hemograma completo: Hemácias 4.5 milhões/mm³...",
                "category": "laudo",
                "document_type": "exame_sangue"
            }
        }


class ValidateTextRequest(BaseModel):
    """Requisição para validação de texto"""
    text: str = Field(..., min_length=10, max_length=10000, description="Texto para validar")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hemograma completo: Hemácias 4.5 milhões/mm³..."
            }
        }


class UsageSessionRequest(BaseModel):
    """Requisição para criar/atualizar sessão de uso"""
    session_id: Optional[str] = Field(None, description="ID da sessão existente")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123"
            }
        }
