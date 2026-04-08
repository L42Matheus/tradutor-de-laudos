"""
Routes for epidemiological document processing and anonymized metadata capture.
"""
import base64
import hashlib
import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.config import get_settings
from app.database import get_db, get_db_context
from app.models.db_models import EpidemiologiaMetadado, Traducao, User
from app.services.auth_service import get_current_user_optional
from app.services.geocodificacao_service import geocodificar, geocodificar_municipio
from app.services.history_service import generate_file_hash, register_translation_history
from app.services.lgpd_service import sanitizar_metadados
from app.services.parser_service import detectar_tipo_mime, parse_entrada
from app.services.traducao_epidemio_service import processar_laudo
from app.utils.datetime_utils import brazil_now, serialize_brazil_datetime


router = APIRouter()
settings = get_settings()


class ProcessarResponse(BaseModel):
    """Response payload for epidemiology processing."""

    success: bool
    resumo: Optional[str] = None
    detalhado: Optional[str] = None
    entenda_facil: Optional[str] = None
    texto_traduzido: Optional[str] = None
    glossario: dict[str, str] = Field(default_factory=dict)
    alertas: list[str] = Field(default_factory=list)
    condicao_categoria: Optional[str] = None
    faixa_etaria: Optional[str] = None
    id: Optional[str] = None
    requer_confirmacao_localizacao: bool = False
    from_cache: bool = False
    documento_repetido: bool = False
    total_acessos: int = 1
    ultimo_acesso_em: Optional[str] = None
    error: Optional[str] = None


class ConfirmarLocalizacaoRequest(BaseModel):
    """Request payload for manual location confirmation."""

    traducao_id: str
    municipio: str
    estado: str
    municipio_ibge_id: Optional[str] = None


async def _persistir_metadados_automaticos(traducao_id: str, resultado_traducao: dict) -> None:
    """
    Try to resolve location automatically without blocking the main response.
    """
    nome_clinica = resultado_traducao.get("nome_clinica")
    if not nome_clinica:
        return

    geo = await geocodificar(nome_clinica)
    metadado_sanitizado = sanitizar_metadados(resultado_traducao, geo)
    if not metadado_sanitizado:
        return

    with get_db_context() as db:
        traducao = db.query(Traducao).filter(Traducao.id == traducao_id).first()
        if not traducao or traducao.metadado:
            return

        metadado = EpidemiologiaMetadado(
            traducao_id=traducao.id,
            municipio=metadado_sanitizado["municipio"],
            estado=metadado_sanitizado["estado"],
            lat=metadado_sanitizado["lat"],
            lon=metadado_sanitizado["lon"],
            condicao_categoria=metadado_sanitizado["condicao_categoria"],
            faixa_etaria=metadado_sanitizado["faixa_etaria"],
            mes_ano=metadado_sanitizado["mes_ano"],
        )
        db.add(metadado)


def _gerar_documento_hash(texto_extraido: str) -> str:
    texto_normalizado = " ".join(texto_extraido.split()).strip().lower()
    return hashlib.sha256(texto_normalizado.encode("utf-8")).hexdigest()


def _carregar_glossario(traducao: Traducao, glossario_fallback: dict[str, str]) -> dict[str, str]:
    if glossario_fallback:
        return glossario_fallback

    if traducao.glossario_json:
        try:
            return json.loads(traducao.glossario_json)
        except json.JSONDecodeError:
            return {}

    return {}


def _carregar_resultado_traducao(traducao: Traducao) -> dict:
    if traducao.resultado_json:
        try:
            resultado = json.loads(traducao.resultado_json)
            if isinstance(resultado, dict):
                return resultado
        except json.JSONDecodeError:
            pass

    glossario = _carregar_glossario(traducao, {})
    return {
        "resumo": traducao.texto_traduzido,
        "detalhado": traducao.texto_traduzido,
        "entenda_facil": traducao.texto_traduzido,
        "texto_traduzido": traducao.texto_traduzido,
        "glossario": glossario,
        "alertas": [],
        "condicao_categoria": traducao.condicao_categoria,
        "faixa_etaria": traducao.metadado.faixa_etaria if traducao.metadado else None,
        "from_cache": True,
    }


def _buscar_traducao_existente(
    db: Session,
    documento_hash: str,
    session_id: Optional[str],
    current_user: Optional[User],
) -> Optional[Traducao]:
    query = db.query(Traducao).filter(Traducao.documento_hash == documento_hash)

    if current_user:
        if session_id:
            return query.filter(
                or_(Traducao.user_id == current_user.id, Traducao.session_id == session_id)
            ).first()
        return query.filter(Traducao.user_id == current_user.id).first()

    if session_id:
        return query.filter(Traducao.session_id == session_id).first()

    return None


def _montar_resposta(
    traducao: Traducao,
    resultado_traducao: dict,
    glossario: dict[str, str],
    requer_confirmacao: bool,
    documento_repetido: bool,
) -> ProcessarResponse:
    ultimo_acesso = traducao.ultimo_acesso_em or traducao.criado_em
    return ProcessarResponse(
        success=True,
        resumo=resultado_traducao.get("resumo") or traducao.texto_traduzido,
        detalhado=resultado_traducao.get("detalhado") or traducao.texto_traduzido,
        entenda_facil=resultado_traducao.get("entenda_facil") or traducao.texto_traduzido,
        texto_traduzido=traducao.texto_traduzido or resultado_traducao["texto_traduzido"],
        glossario=glossario,
        alertas=resultado_traducao.get("alertas") or [],
        condicao_categoria=traducao.condicao_categoria or resultado_traducao.get("condicao_categoria"),
        faixa_etaria=resultado_traducao.get("faixa_etaria"),
        id=traducao.id,
        requer_confirmacao_localizacao=requer_confirmacao,
        from_cache=resultado_traducao.get("from_cache", False),
        documento_repetido=documento_repetido,
        total_acessos=traducao.total_acessos or 1,
        ultimo_acesso_em=serialize_brazil_datetime(ultimo_acesso) if ultimo_acesso else None,
    )


@router.post("/processar", response_model=ProcessarResponse)
async def processar_documento(
    background_tasks: BackgroundTasks,
    arquivo: Optional[UploadFile] = File(None, description="Arquivo do laudo (PDF ou imagem)"),
    texto: Optional[str] = Form(None, description="Texto do laudo (se nao houver arquivo)"),
    municipio_confirmado: Optional[str] = Form(
        None, description="Municipio confirmado pelo usuario"
    ),
    estado_confirmado: Optional[str] = Form(None, description="Estado confirmado pelo usuario"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ProcessarResponse:
    """Process a medical document and persist anonymized epidemiology metadata when possible."""
    if not settings.anthropic_api_key:
        return ProcessarResponse(success=False, error="API key nao configurada")

    try:
        texto_extraido, erro_parse = await parse_entrada(arquivo, texto)
        if erro_parse:
            return ProcessarResponse(success=False, error=erro_parse)

        if not texto_extraido or not texto_extraido.strip():
            return ProcessarResponse(success=False, error="Nenhum texto extraido do documento")

        original_image_base64 = None
        original_image_media_type = None
        file_hash = None
        mime_type = detectar_tipo_mime(arquivo) if arquivo else None
        history_input_type = "text"
        if arquivo and mime_type and mime_type.startswith("image/"):
            image_bytes = await arquivo.read()
            await arquivo.seek(0)
            original_image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")
            original_image_media_type = mime_type
            file_hash = generate_file_hash(image_bytes)
            history_input_type = "image"
        elif arquivo:
            file_bytes = await arquivo.read()
            await arquivo.seek(0)
            file_hash = generate_file_hash(file_bytes)
            history_input_type = "text"

        traducao_existente = _buscar_traducao_existente(
            db,
            _gerar_documento_hash(texto_extraido),
            x_session_id,
            current_user,
        )

        documento_repetido = traducao_existente is not None
        requer_confirmacao = False

        if traducao_existente:
            traducao = traducao_existente
            if current_user and not traducao.user_id:
                traducao.user_id = current_user.id
            if x_session_id and not traducao.session_id:
                traducao.session_id = x_session_id

            traducao.ultimo_acesso_em = brazil_now()
            traducao.total_acessos = (traducao.total_acessos or 1) + 1
            traducao.cache_hits = (traducao.cache_hits or 0) + 1

            resultado_traducao = _carregar_resultado_traducao(traducao)
            glossario = _carregar_glossario(traducao, resultado_traducao.get("glossario", {}))
            resultado_traducao["glossario"] = glossario
            resultado_traducao["from_cache"] = True

            if municipio_confirmado and estado_confirmado and not traducao.metadado:
                geo = await geocodificar_municipio(municipio_confirmado, estado_confirmado)
                if geo:
                    metadado = EpidemiologiaMetadado(
                        traducao_id=traducao.id,
                        municipio=geo["municipio"],
                        estado=geo["estado"],
                        lat=geo["lat"],
                        lon=geo["lon"],
                        condicao_categoria=traducao.condicao_categoria or "outro",
                        faixa_etaria=resultado_traducao.get("faixa_etaria") or "nao_informado",
                        mes_ano=date.today().replace(day=1),
                    )
                    db.add(metadado)
                else:
                    requer_confirmacao = True
            else:
                requer_confirmacao = traducao.metadado is None
        else:
            documento_hash = _gerar_documento_hash(texto_extraido)
            resultado_traducao = await processar_laudo(texto_extraido)
            glossario = resultado_traducao.get("glossario", {})
            traducao = Traducao(
                session_id=x_session_id,
                user_id=current_user.id if current_user else None,
                documento_hash=documento_hash,
                texto_original=texto_extraido[:10000],
                texto_traduzido=resultado_traducao["texto_traduzido"],
                resultado_json=json.dumps(resultado_traducao, ensure_ascii=True),
                glossario_json=json.dumps(glossario) if glossario else None,
                condicao_categoria=resultado_traducao["condicao_categoria"],
                ultimo_acesso_em=brazil_now(),
                total_acessos=1,
                cache_hits=1 if resultado_traducao.get("from_cache", False) else 0,
            )
            db.add(traducao)
            db.flush()

            if municipio_confirmado and estado_confirmado and not traducao.metadado:
                geo = await geocodificar_municipio(municipio_confirmado, estado_confirmado)
                metadado_sanitizado = sanitizar_metadados(resultado_traducao, geo)

                if metadado_sanitizado:
                    metadado = EpidemiologiaMetadado(
                        traducao_id=traducao.id,
                        municipio=metadado_sanitizado["municipio"],
                        estado=metadado_sanitizado["estado"],
                        lat=metadado_sanitizado["lat"],
                        lon=metadado_sanitizado["lon"],
                        condicao_categoria=metadado_sanitizado["condicao_categoria"],
                        faixa_etaria=metadado_sanitizado["faixa_etaria"],
                        mes_ano=metadado_sanitizado["mes_ano"],
                    )
                    db.add(metadado)
                else:
                    requer_confirmacao = True
            elif traducao.metadado:
                requer_confirmacao = False
            elif not resultado_traducao.get("nome_clinica"):
                requer_confirmacao = True
            else:
                background_tasks.add_task(
                    _persistir_metadados_automaticos,
                    traducao.id,
                    resultado_traducao,
                )

        glossario = _carregar_glossario(traducao, resultado_traducao.get("glossario", {}))

        result_payload = {
            **resultado_traducao,
            "documento_repetido": documento_repetido,
            "total_acessos": traducao.total_acessos or 1,
        }
        register_translation_history(
            db=db,
            user=current_user,
            source="epidemio_processar",
            input_type=history_input_type,
            document_category=resultado_traducao.get("condicao_categoria"),
            document_type="epidemiologico",
            original_text=texto_extraido,
            original_image_base64=original_image_base64,
            original_image_media_type=original_image_media_type,
            result_payload=result_payload,
            file_hash=file_hash,
        )

        db.commit()
        db.refresh(traducao)

        return _montar_resposta(
            traducao=traducao,
            resultado_traducao=resultado_traducao,
            glossario=glossario,
            requer_confirmacao=requer_confirmacao,
            documento_repetido=documento_repetido,
        )

    except ValueError as exc:
        return ProcessarResponse(success=False, error=str(exc))
    except Exception as exc:
        db.rollback()
        return ProcessarResponse(success=False, error=f"Erro ao processar documento: {exc}")


@router.post("/confirmar-localizacao", response_model=ProcessarResponse)
async def confirmar_localizacao(
    request: ConfirmarLocalizacaoRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: Session = Depends(get_db),
) -> ProcessarResponse:
    """Confirm location for an already processed translation."""
    del x_session_id

    try:
        traducao = db.query(Traducao).filter(Traducao.id == request.traducao_id).first()
        if not traducao:
            return ProcessarResponse(success=False, error="Traducao nao encontrada")

        glossario = _carregar_glossario(traducao, {})

        if traducao.metadado:
            return _montar_resposta(
                traducao=traducao,
                resultado_traducao={"faixa_etaria": None, "from_cache": False},
                glossario=glossario,
                requer_confirmacao=False,
                documento_repetido=False,
            )

        geo = await geocodificar_municipio(
            request.municipio,
            request.estado,
            request.municipio_ibge_id,
        )
        if not geo:
            return ProcessarResponse(
                success=False,
                error="Nao foi possivel geocodificar o municipio informado",
            )

        metadado = EpidemiologiaMetadado(
            traducao_id=traducao.id,
            municipio=geo["municipio"],
            estado=geo["estado"],
            lat=geo["lat"],
            lon=geo["lon"],
            condicao_categoria=traducao.condicao_categoria or "outro",
            faixa_etaria="nao_informado",
            mes_ano=date.today().replace(day=1),
        )
        db.add(metadado)
        db.commit()
        db.refresh(traducao)

        return _montar_resposta(
            traducao=traducao,
            resultado_traducao={"faixa_etaria": None, "from_cache": False},
            glossario=glossario,
            requer_confirmacao=False,
            documento_repetido=False,
        )

    except Exception as exc:
        db.rollback()
        return ProcessarResponse(success=False, error=f"Erro ao confirmar localizacao: {exc}")
