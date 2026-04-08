"""
Rotas para gerenciamento de providers de LLM
Permite ao usuário ver e selecionar qual provider/modelo usar
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.services.auth_service import get_current_user
from app.models.db_models import User
from app.models.enums import LLMProvider, LLM_PROVIDER_LABELS, LLM_PROVIDER_DESCRIPTIONS
from app.services.llm_providers.models import get_all_models, get_models_for_provider, get_model_info


router = APIRouter(prefix="/providers", tags=["providers"])


# ============== Response Models ==============

class ProviderInfo(BaseModel):
    """Informações de um provider"""
    id: str
    name: str
    description: str
    enabled: bool
    default_model: str


class ProvidersListResponse(BaseModel):
    """Lista de providers disponíveis"""
    success: bool
    data: list[ProviderInfo]
    default_provider: str


class UserPreferenceRequest(BaseModel):
    """Request para atualizar preferência do usuário"""
    provider: str
    model: str | None = None  # Opcional - se não informado, usa o recomendado


class UserPreferenceResponse(BaseModel):
    """Resposta com preferência do usuário"""
    success: bool
    provider: str
    model: str | None


# ============== Helper Functions ==============

def is_provider_enabled(provider_id: str) -> bool:
    """Verifica se um provider está habilitado (tem API key configurada)"""
    settings = get_settings()

    if provider_id not in settings.enabled_providers:
        return False

    key_mapping = {
        "claude": settings.anthropic_api_key,
        "openai": settings.openai_api_key,
        "gemini": settings.google_api_key,
    }

    api_key = key_mapping.get(provider_id, "")
    return bool(api_key and api_key.strip())


def get_default_model(provider_id: str) -> str:
    """Retorna o modelo padrão para um provider"""
    settings = get_settings()

    model_mapping = {
        "claude": settings.claude_model,
        "openai": settings.openai_model,
        "gemini": settings.gemini_model,
    }

    return model_mapping.get(provider_id, "")


# ============== Endpoints ==============

@router.get("", response_model=ProvidersListResponse)
async def list_providers():
    """
    Lista todos os providers de LLM disponíveis

    Retorna informações sobre cada provider, incluindo:
    - Se está habilitado (tem API key configurada)
    - Modelo padrão
    - Descrição

    Não requer autenticação - informação pública
    """
    settings = get_settings()
    providers_list = []

    for provider_enum in LLMProvider:
        provider_id = provider_enum.value
        enabled = is_provider_enabled(provider_id)

        providers_list.append(ProviderInfo(
            id=provider_id,
            name=LLM_PROVIDER_LABELS.get(provider_enum, provider_id),
            description=LLM_PROVIDER_DESCRIPTIONS.get(provider_enum, ""),
            enabled=enabled,
            default_model=get_default_model(provider_id) if enabled else "",
        ))

    # Determina o provider padrão (primeiro habilitado)
    default = "claude"
    for p in providers_list:
        if p.enabled:
            default = p.id
            break

    return ProvidersListResponse(
        success=True,
        data=providers_list,
        default_provider=default,
    )


@router.get("/enabled")
async def list_enabled_providers():
    """
    Lista apenas os providers habilitados (com API key configurada)

    Útil para popular dropdowns no frontend
    """
    settings = get_settings()
    enabled = []

    for provider_enum in LLMProvider:
        provider_id = provider_enum.value
        if is_provider_enabled(provider_id):
            enabled.append({
                "id": provider_id,
                "name": LLM_PROVIDER_LABELS.get(provider_enum, provider_id),
                "model": get_default_model(provider_id),
            })

    return {
        "success": True,
        "data": enabled,
    }


@router.get("/models")
async def list_all_models():
    """
    Lista todos os modelos disponíveis por provider.

    Retorna informações detalhadas sobre cada modelo:
    - ID do modelo (para usar na API)
    - Nome amigável
    - Descrição
    - Se suporta visão/texto
    - Se é o recomendado
    - Tier de custo (economy, standard, premium)
    """
    return {
        "success": True,
        "data": get_all_models(),
    }


@router.get("/models/{provider}")
async def list_provider_models(provider: str):
    """
    Lista modelos disponíveis para um provider específico.
    """
    if provider not in ["claude", "openai", "gemini"]:
        raise HTTPException(
            status_code=400,
            detail=f"Provider inválido: {provider}"
        )

    models = get_models_for_provider(provider)
    return {
        "success": True,
        "provider": provider,
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "supports_vision": m.supports_vision,
                "is_recommended": m.is_recommended,
                "cost_tier": m.cost_tier,
            }
            for m in models
        ],
    }


@router.get("/health/{provider}")
async def check_provider_health(provider: str):
    """
    Verifica se um provider está funcionando

    Args:
        provider: 'claude', 'openai', ou 'gemini'

    Returns:
        Status de saúde do provider
    """
    if provider not in ["claude", "openai", "gemini"]:
        raise HTTPException(
            status_code=400,
            detail=f"Provider inválido: {provider}. Use: claude, openai, gemini"
        )

    if not is_provider_enabled(provider):
        return {
            "success": False,
            "provider": provider,
            "healthy": False,
            "error": "Provider não configurado (API key ausente)",
        }

    # Tenta instanciar o provider para verificar se funciona
    try:
        from app.services.llm_providers.router import LLMRouter
        llm_provider = LLMRouter.get_provider(provider)

        return {
            "success": True,
            "provider": provider,
            "healthy": True,
            "model": get_default_model(provider),
        }
    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "healthy": False,
            "error": str(e),
        }


@router.get("/preference", response_model=UserPreferenceResponse)
async def get_user_preference(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna a preferência de provider do usuário logado

    Requer autenticação
    """
    provider = getattr(current_user, 'preferred_llm_provider', 'claude') or 'claude'
    model = getattr(current_user, 'preferred_llm_model', None)

    return UserPreferenceResponse(
        success=True,
        provider=provider,
        model=model,
    )


@router.put("/preference", response_model=UserPreferenceResponse)
async def update_user_preference(
    request: UserPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza a preferência de provider e modelo do usuário

    Requer autenticação. O provider deve estar habilitado.
    Se model não for informado, usa o modelo recomendado do provider.
    """
    provider = request.provider.lower()

    # Valida o provider
    if provider not in ["claude", "openai", "gemini"]:
        raise HTTPException(
            status_code=400,
            detail=f"Provider inválido: {request.provider}. Use: claude, openai, gemini"
        )

    if not is_provider_enabled(provider):
        raise HTTPException(
            status_code=400,
            detail=f"Provider {request.provider} não está disponível (API key não configurada)"
        )

    # Valida o modelo se informado
    model_id = request.model
    if model_id:
        model_info = get_model_info(provider, model_id)
        if not model_info:
            available = [m.id for m in get_models_for_provider(provider)]
            raise HTTPException(
                status_code=400,
                detail=f"Modelo inválido: {model_id}. Disponíveis para {provider}: {available}"
            )
    else:
        # Usa o modelo padrão do config
        model_id = get_default_model(provider)

    # Atualiza preferência do usuário
    current_user.preferred_llm_provider = provider
    current_user.preferred_llm_model = model_id

    db.commit()
    db.refresh(current_user)

    return UserPreferenceResponse(
        success=True,
        provider=current_user.preferred_llm_provider,
        model=current_user.preferred_llm_model,
    )
