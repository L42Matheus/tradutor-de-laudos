"""
Rotas de controle de uso (freemium)
"""
from fastapi import APIRouter, Header
from typing import Optional
import uuid

from app.models.responses import UsageResponse, UsageStatus
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# Armazenamento em memória para sessões (em produção usar Redis)
sessions: dict[str, dict] = {}


@router.get("/status", response_model=UsageResponse)
async def get_usage_status(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
) -> UsageResponse:
    """
    Retorna o status de uso da sessão atual.

    - **X-Session-ID**: Header com ID da sessão (opcional)
    """
    session_id = x_session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = {"translations_used": 0}

    used = sessions[session_id]["translations_used"]
    limit = settings.free_translations_limit

    return UsageResponse(
        success=True,
        data=UsageStatus(
            session_id=session_id,
            translations_used=used,
            translations_remaining=max(0, limit - used),
            translations_limit=limit,
            is_limit_reached=used >= limit
        )
    )


@router.post("/increment", response_model=UsageResponse)
async def increment_usage(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
) -> UsageResponse:
    """
    Incrementa o contador de uso da sessão.

    - **X-Session-ID**: Header com ID da sessão
    """
    session_id = x_session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = {"translations_used": 0}

    sessions[session_id]["translations_used"] += 1
    used = sessions[session_id]["translations_used"]
    limit = settings.free_translations_limit

    return UsageResponse(
        success=True,
        data=UsageStatus(
            session_id=session_id,
            translations_used=used,
            translations_remaining=max(0, limit - used),
            translations_limit=limit,
            is_limit_reached=used >= limit
        )
    )


@router.post("/reset", response_model=UsageResponse)
async def reset_usage(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
) -> UsageResponse:
    """
    Reseta o contador de uso da sessão (para testes/admin).

    - **X-Session-ID**: Header com ID da sessão
    """
    session_id = x_session_id or str(uuid.uuid4())
    sessions[session_id] = {"translations_used": 0}
    limit = settings.free_translations_limit

    return UsageResponse(
        success=True,
        data=UsageStatus(
            session_id=session_id,
            translations_used=0,
            translations_remaining=limit,
            translations_limit=limit,
            is_limit_reached=False
        )
    )
