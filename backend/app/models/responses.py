"""
Modelos de resposta Pydantic
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.models.enums import DocumentCategory


class TranslationResult(BaseModel):
    """Resultado da tradução"""
    resumo: str = Field(..., description="Resumo simplificado do documento")
    detalhado: str = Field(..., description="Explicação detalhada")
    entenda_facil: str = Field(..., description="Explicação em linguagem muito simples")
    glossario: Dict[str, str] = Field(default_factory=dict, description="Termos técnicos explicados")
    alertas: List[str] = Field(default_factory=list, description="Alertas importantes")
    is_saude_mental: bool = Field(False, description="Indica se é documento de saúde mental")


class TranslateResponse(BaseModel):
    """Resposta da tradução"""
    success: bool = Field(..., description="Se a tradução foi bem sucedida")
    data: Optional[TranslationResult] = Field(None, description="Resultado da tradução")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")
    anonymized_fields: List[str] = Field(default_factory=list, description="Campos anonimizados")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "resumo": "Seus exames de sangue estão dentro da normalidade...",
                    "detalhado": "O hemograma mostra valores adequados...",
                    "entenda_facil": "Pense no sangue como um time de futebol...",
                    "glossario": {"Hemácias": "São as células vermelhas do sangue..."},
                    "alertas": [],
                    "is_saude_mental": False
                },
                "error": None,
                "anonymized_fields": ["CPF", "Nome"]
            }
        }


class ValidationResult(BaseModel):
    """Resultado da validação"""
    is_valid: bool = Field(..., description="Se o documento é válido")
    document_type: Optional[str] = Field(None, description="Tipo detectado do documento")
    suggested_category: Optional[DocumentCategory] = Field(None, description="Categoria sugerida")
    message: str = Field(..., description="Mensagem explicativa")


class ValidateResponse(BaseModel):
    """Resposta da validação"""
    success: bool = Field(..., description="Se a validação foi executada")
    data: Optional[ValidationResult] = Field(None, description="Resultado da validação")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")


class UsageStatus(BaseModel):
    """Status de uso da sessão"""
    session_id: str = Field(..., description="ID da sessão")
    translations_used: int = Field(..., description="Traduções já utilizadas")
    translations_remaining: int = Field(..., description="Traduções restantes")
    translations_limit: int = Field(..., description="Limite total de traduções")
    is_limit_reached: bool = Field(..., description="Se o limite foi atingido")


class UsageResponse(BaseModel):
    """Resposta do status de uso"""
    success: bool
    data: Optional[UsageStatus] = None
    error: Optional[str] = None


class SupportQuote(BaseModel):
    """Frase de apoio emocional"""
    quote: str = Field(..., description="Frase motivacional")
    author: Optional[str] = Field(None, description="Autor da frase")


class BreathingExercise(BaseModel):
    """Exercício de respiração"""
    name: str = Field(..., description="Nome do exercício")
    description: str = Field(..., description="Como fazer o exercício")
    steps: List[str] = Field(..., description="Passos do exercício")


class SupportResource(BaseModel):
    """Recurso de apoio"""
    name: str = Field(..., description="Nome do recurso")
    description: str = Field(..., description="Descrição do recurso")
    contact: str = Field(..., description="Contato ou link")
    is_emergency: bool = Field(False, description="Se é recurso de emergência")


class SupportResponse(BaseModel):
    """Resposta de recursos de apoio"""
    quotes: List[SupportQuote] = Field(default_factory=list)
    exercises: List[BreathingExercise] = Field(default_factory=list)
    resources: List[SupportResource] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str
    app: str
    version: str
