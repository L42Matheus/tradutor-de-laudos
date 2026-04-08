"""
Rotas para revisao de traducoes por especialistas.
Inclui fila de revisao, parecer e estatisticas.
"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import (
    User, Traducao, RevisaoEspecialista, StatusRevisao
)
from app.models.platform_models import Translation as PlatformTranslation, TranslationReview
from app.services.auth_service import get_current_user


router = APIRouter()


# === Schemas ===

class TraducaoFilaItem(BaseModel):
    id: str
    texto_original_preview: str
    condicao_categoria: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


class TraducaoDetalhe(BaseModel):
    id: str
    texto_original: str
    texto_traduzido: str
    condicao_categoria: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


class ParecerRequest(BaseModel):
    traducao_id: str
    nota_fidelidade: float = Field(..., ge=1, le=5)
    nota_clareza: float = Field(..., ge=1, le=5)
    nota_risco: float = Field(..., ge=1, le=5)
    comentario_tecnico: Optional[str] = None
    sugestao_correcao: Optional[str] = None


class ParecerResponse(BaseModel):
    success: bool
    message: str
    revisao_id: Optional[str] = None


class FilaResponse(BaseModel):
    success: bool
    total: int
    items: List[TraducaoFilaItem]


class EstatisticasResponse(BaseModel):
    success: bool
    total_revisoes: int
    media_fidelidade: float
    media_clareza: float
    media_risco: float
    media_geral: float


class SolicitarRevisaoRequest(BaseModel):
    traducao_id: str


class SolicitarRevisaoResponse(BaseModel):
    success: bool
    message: str


# === Helpers ===

def verificar_especialista(user: User) -> None:
    """Verifica se o usuario e especialista verificado."""
    if user.role != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a especialistas"
        )
    if user.specialist_verification_status != "verified":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Especialista ainda nao verificado"
        )


def buscar_traducao_plataforma(db: Session, traducao_id: str) -> Optional[PlatformTranslation]:
    return (
        db.query(PlatformTranslation)
        .filter(PlatformTranslation.legacy_source_table == "traducoes")
        .filter(PlatformTranslation.legacy_source_id == traducao_id)
        .first()
    )


# === Endpoints ===

@router.post("/solicitar", response_model=SolicitarRevisaoResponse)
async def solicitar_revisao(
    request: SolicitarRevisaoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SolicitarRevisaoResponse:
    """
    Solicita revisao de especialista para uma traducao.
    Disponivel para qualquer usuario autenticado.
    """
    traducao = db.query(Traducao).filter(
        Traducao.id == request.traducao_id,
        Traducao.user_id == current_user.id
    ).first()

    if not traducao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traducao nao encontrada"
        )

    if traducao.solicitar_revisao:
        return SolicitarRevisaoResponse(
            success=True,
            message="Revisao ja foi solicitada para esta traducao"
        )

    traducao.solicitar_revisao = True
    traducao.status_revisao = StatusRevisao.PENDENTE.value
    traducao_plataforma = buscar_traducao_plataforma(db, traducao.id)
    if traducao_plataforma:
        traducao_plataforma.specialist_review_requested = True
        traducao_plataforma.specialist_review_status = StatusRevisao.PENDENTE.value
    db.commit()

    return SolicitarRevisaoResponse(
        success=True,
        message="Revisao solicitada com sucesso"
    )


@router.get("/fila", response_model=FilaResponse)
async def listar_fila_revisao(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> FilaResponse:
    """
    Lista traducoes pendentes de revisao.
    Apenas para especialistas verificados.
    """
    verificar_especialista(current_user)

    query = db.query(Traducao).filter(
        Traducao.solicitar_revisao == True,
        Traducao.status_revisao == StatusRevisao.PENDENTE.value
    ).order_by(Traducao.criado_em.asc())

    total = query.count()
    traducoes = query.offset(offset).limit(limit).all()

    items = [
        TraducaoFilaItem(
            id=t.id,
            texto_original_preview=t.texto_original[:150] + "..." if len(t.texto_original) > 150 else t.texto_original,
            condicao_categoria=t.condicao_categoria,
            criado_em=t.criado_em
        )
        for t in traducoes
    ]

    return FilaResponse(success=True, total=total, items=items)


@router.get("/traducao/{traducao_id}", response_model=TraducaoDetalhe)
async def obter_traducao_para_revisao(
    traducao_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TraducaoDetalhe:
    """
    Obtem detalhes de uma traducao para revisao.
    Marca como 'em_revisao' se estiver pendente.
    """
    verificar_especialista(current_user)

    traducao = db.query(Traducao).filter(Traducao.id == traducao_id).first()

    if not traducao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traducao nao encontrada"
        )

    if not traducao.solicitar_revisao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta traducao nao foi enviada para revisao"
        )

    if traducao.status_revisao == StatusRevisao.PENDENTE.value:
        traducao.status_revisao = StatusRevisao.EM_REVISAO.value
        traducao_plataforma = buscar_traducao_plataforma(db, traducao.id)
        if traducao_plataforma:
            traducao_plataforma.specialist_review_status = StatusRevisao.EM_REVISAO.value
        db.commit()

    return TraducaoDetalhe(
        id=traducao.id,
        texto_original=traducao.texto_original,
        texto_traduzido=traducao.texto_traduzido,
        condicao_categoria=traducao.condicao_categoria,
        criado_em=traducao.criado_em
    )


@router.post("/parecer", response_model=ParecerResponse)
async def enviar_parecer(
    request: ParecerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ParecerResponse:
    """
    Envia parecer tecnico sobre uma traducao.
    """
    verificar_especialista(current_user)

    traducao = db.query(Traducao).filter(Traducao.id == request.traducao_id).first()

    if not traducao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traducao nao encontrada"
        )

    if traducao.revisao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta traducao ja foi revisada"
        )

    nota_geral = (request.nota_fidelidade + request.nota_clareza + request.nota_risco) / 3

    revisao = RevisaoEspecialista(
        traducao_id=traducao.id,
        especialista_id=current_user.id,
        nota_fidelidade=request.nota_fidelidade,
        nota_clareza=request.nota_clareza,
        nota_risco=request.nota_risco,
        nota_geral=round(nota_geral, 2),
        comentario_tecnico=request.comentario_tecnico,
        sugestao_correcao=request.sugestao_correcao
    )

    traducao.status_revisao = StatusRevisao.CONCLUIDA.value
    traducao_plataforma = buscar_traducao_plataforma(db, traducao.id)
    if traducao_plataforma:
        traducao_plataforma.specialist_review_requested = True
        traducao_plataforma.specialist_review_status = StatusRevisao.CONCLUIDA.value

    db.add(revisao)
    if traducao_plataforma and not traducao_plataforma.review:
        db.add(
            TranslationReview(
                translation_id=traducao_plataforma.id,
                specialist_id=current_user.id,
                fidelity_score=request.nota_fidelidade,
                clarity_score=request.nota_clareza,
                risk_score=request.nota_risco,
                overall_score=round(nota_geral, 2),
                technical_comment=request.comentario_tecnico,
                correction_suggestion=request.sugestao_correcao,
            )
        )
    db.commit()

    return ParecerResponse(
        success=True,
        message="Parecer registrado com sucesso",
        revisao_id=revisao.id
    )


@router.get("/minhas", response_model=FilaResponse)
async def listar_minhas_revisoes(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> FilaResponse:
    """
    Lista revisoes feitas pelo especialista logado.
    """
    verificar_especialista(current_user)

    query = db.query(Traducao).join(RevisaoEspecialista).filter(
        RevisaoEspecialista.especialista_id == current_user.id
    ).order_by(RevisaoEspecialista.criado_em.desc())

    total = query.count()
    traducoes = query.offset(offset).limit(limit).all()

    items = [
        TraducaoFilaItem(
            id=t.id,
            texto_original_preview=t.texto_original[:150] + "..." if len(t.texto_original) > 150 else t.texto_original,
            condicao_categoria=t.condicao_categoria,
            criado_em=t.criado_em
        )
        for t in traducoes
    ]

    return FilaResponse(success=True, total=total, items=items)


@router.get("/estatisticas", response_model=EstatisticasResponse)
async def obter_estatisticas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> EstatisticasResponse:
    """
    Obtem estatisticas das revisoes do especialista.
    """
    verificar_especialista(current_user)

    revisoes = db.query(RevisaoEspecialista).filter(
        RevisaoEspecialista.especialista_id == current_user.id
    ).all()

    if not revisoes:
        return EstatisticasResponse(
            success=True,
            total_revisoes=0,
            media_fidelidade=0,
            media_clareza=0,
            media_risco=0,
            media_geral=0
        )

    total = len(revisoes)
    media_fidelidade = sum(r.nota_fidelidade for r in revisoes) / total
    media_clareza = sum(r.nota_clareza for r in revisoes) / total
    media_risco = sum(r.nota_risco for r in revisoes) / total
    media_geral = sum(r.nota_geral for r in revisoes) / total

    return EstatisticasResponse(
        success=True,
        total_revisoes=total,
        media_fidelidade=round(media_fidelidade, 2),
        media_clareza=round(media_clareza, 2),
        media_risco=round(media_risco, 2),
        media_geral=round(media_geral, 2)
    )
