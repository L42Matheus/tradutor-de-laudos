"""
Persistencia canÃ´nica de documentos, versÃµes, traduÃ§Ãµes e alertas.

Essa camada prepara o backend para Postgres + RAG sem quebrar os fluxos legados.
"""
import hashlib
import json
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.platform_models import ClinicalAlert, Document, DocumentAsset, DocumentVersion, Translation
from app.services.clinical_alerts_service import derive_alert_candidates
from app.services.storage_service import StorageService
from app.utils.datetime_utils import brazil_now


settings = get_settings()
storage_service = StorageService()


def _normalize_text(text: Optional[str]) -> Optional[str]:
    if not text or not text.strip():
        return None
    return " ".join(text.split()).strip()


def compute_text_hash(text: Optional[str]) -> Optional[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return None
    return hashlib.sha256(normalized.lower().encode("utf-8")).hexdigest()


def compute_file_hash(file_bytes: Optional[bytes]) -> Optional[str]:
    if not file_bytes:
        return None
    return hashlib.sha256(file_bytes).hexdigest()


def _find_document(
    db: Session,
    *,
    canonical_hash: Optional[str],
    user_id: Optional[str],
    session_id: Optional[str],
) -> Optional[Document]:
    if not canonical_hash:
        return None

    query = db.query(Document).filter(Document.canonical_hash == canonical_hash)
    if user_id and session_id:
        query = query.filter(or_(Document.owner_user_id == user_id, Document.session_id == session_id))
    elif user_id:
        query = query.filter(Document.owner_user_id == user_id)
    elif session_id:
        query = query.filter(Document.session_id == session_id)

    return query.order_by(Document.updated_at.desc()).first()


def _upsert_asset(
    db: Session,
    *,
    document: Document,
    input_type: str,
    file_bytes: Optional[bytes],
    file_name: Optional[str],
    media_type: Optional[str],
    file_hash: Optional[str],
) -> Optional[DocumentAsset]:
    if not file_bytes or not file_hash:
        return None

    kind = "original_image" if input_type == "image" else "original_file"
    existing = (
        db.query(DocumentAsset)
        .filter(DocumentAsset.document_id == document.id)
        .filter(DocumentAsset.kind == kind)
        .filter(DocumentAsset.checksum_sha256 == file_hash)
        .first()
    )
    if existing:
        return existing

    stored = storage_service.save_bytes(
        document_id=document.id,
        asset_kind=kind,
        data=file_bytes,
        file_name=file_name,
        media_type=media_type,
    )
    asset = DocumentAsset(
        document_id=document.id,
        kind=kind,
        storage_backend=stored.storage_backend,
        storage_key=stored.storage_key,
        media_type=media_type,
        file_name=file_name,
        byte_size=stored.byte_size,
        checksum_sha256=stored.checksum_sha256,
    )
    db.add(asset)
    return asset


def _upsert_document_version(
    db: Session,
    *,
    document: Document,
    input_type: str,
    original_text: Optional[str],
    anonymized_text: Optional[str],
    anonymized_fields: Optional[list],
    file_hash: Optional[str],
    content_hash: Optional[str],
    parser_provider: Optional[str] = None,
    parser_version: Optional[str] = None,
) -> DocumentVersion:
    query = db.query(DocumentVersion).filter(DocumentVersion.document_id == document.id)
    if file_hash:
        version = query.filter(DocumentVersion.file_hash == file_hash).first()
        if version:
            return version
    if content_hash:
        version = query.filter(DocumentVersion.content_hash == content_hash).first()
        if version:
            return version

    next_version = (
        db.query(func.max(DocumentVersion.version_number))
        .filter(DocumentVersion.document_id == document.id)
        .scalar()
        or 0
    ) + 1

    version = DocumentVersion(
        document_id=document.id,
        version_number=next_version,
        file_hash=file_hash,
        content_hash=content_hash,
        input_type=input_type,
        extracted_text=original_text,
        normalized_text=_normalize_text(original_text),
        anonymized_text=anonymized_text,
        anonymized_fields_json=json.dumps(anonymized_fields, ensure_ascii=True) if anonymized_fields else None,
        parser_provider=parser_provider,
        parser_version=parser_version,
    )
    db.add(version)
    db.flush()
    return version


def upsert_translation_record(
    db: Session,
    *,
    user_id: Optional[str],
    session_id: Optional[str],
    source_route: str,
    input_type: str,
    document_category: Optional[str],
    document_type: Optional[str],
    original_text: Optional[str],
    result_payload: dict,
    file_bytes: Optional[bytes] = None,
    file_name: Optional[str] = None,
    media_type: Optional[str] = None,
    anonymized_text: Optional[str] = None,
    anonymized_fields: Optional[list] = None,
    file_hash: Optional[str] = None,
    document_hash: Optional[str] = None,
    provider: Optional[str] = "anthropic",
    model_name: Optional[str] = None,
    prompt_version: Optional[str] = None,
    pipeline_name: Optional[str] = None,
    pipeline_version: Optional[str] = None,
    requires_location_confirmation: bool = False,
    specialist_review_requested: bool = False,
    specialist_review_status: str = "nao_solicitada",
    legacy_source_table: Optional[str] = None,
    legacy_source_id: Optional[str] = None,
) -> Translation:
    normalized_text = _normalize_text(original_text)
    text_hash = document_hash or compute_text_hash(normalized_text)
    effective_file_hash = file_hash or compute_file_hash(file_bytes)
    canonical_hash = effective_file_hash or text_hash

    document = _find_document(
        db,
        canonical_hash=canonical_hash,
        user_id=user_id,
        session_id=session_id,
    )
    if not document:
        document = Document(
            owner_user_id=user_id,
            session_id=session_id,
            source_route=source_route,
            document_category=document_category,
            document_type=document_type,
            input_type=input_type,
            canonical_hash=canonical_hash,
        )
        db.add(document)
        db.flush()
    else:
        document.source_route = source_route
        document.document_category = document_category
        document.document_type = document_type
        document.input_type = input_type
        document.updated_at = brazil_now()

    _upsert_asset(
        db,
        document=document,
        input_type=input_type,
        file_bytes=file_bytes,
        file_name=file_name,
        media_type=media_type,
        file_hash=effective_file_hash,
    )

    version = _upsert_document_version(
        db,
        document=document,
        input_type=input_type,
        original_text=normalized_text,
        anonymized_text=anonymized_text,
        anonymized_fields=anonymized_fields,
        file_hash=effective_file_hash,
        content_hash=text_hash,
        parser_provider="internal",
        parser_version=settings.default_pipeline_version,
    )

    translation = (
        db.query(Translation)
        .filter(Translation.document_version_id == version.id)
        .filter(Translation.source_route == source_route)
        .order_by(Translation.updated_at.desc())
        .first()
    )

    translated_text = (
        result_payload.get("texto_traduzido")
        or result_payload.get("resumo")
        or "Sem traducao disponivel"
    )
    glossary = result_payload.get("glossario") or {}
    model_alerts = result_payload.get("alertas") or []

    common_fields = {
        "user_id": user_id,
        "session_id": session_id,
        "source_route": source_route,
        "legacy_source_table": legacy_source_table,
        "legacy_source_id": legacy_source_id,
        "pipeline_name": pipeline_name or settings.default_pipeline_name,
        "pipeline_version": pipeline_version or settings.default_pipeline_version,
        "provider": provider,
        "model_name": model_name or settings.claude_model,
        "prompt_version": prompt_version or settings.default_pipeline_version,
        "document_category": document_category,
        "document_type": document_type,
        "input_type": input_type,
        "summary": result_payload.get("resumo") or translated_text,
        "detailed": result_payload.get("detalhado") or translated_text,
        "easy_explanation": result_payload.get("entenda_facil") or translated_text,
        "translated_text": translated_text,
        "glossary_json": json.dumps(glossary, ensure_ascii=True) if glossary else None,
        "model_alerts_json": json.dumps(model_alerts, ensure_ascii=True) if model_alerts else None,
        "result_payload_json": json.dumps(result_payload, ensure_ascii=True),
        "is_mental_health": bool(result_payload.get("is_saude_mental", False)),
        "from_cache": bool(result_payload.get("from_cache", False)),
        "requires_location_confirmation": requires_location_confirmation,
        "specialist_review_requested": specialist_review_requested,
        "specialist_review_status": specialist_review_status,
        "epidemiology_category": result_payload.get("condicao_categoria") or document_category,
        "epidemiology_age_band": result_payload.get("faixa_etaria"),
        "last_accessed_at": brazil_now(),
    }

    if translation:
        for key, value in common_fields.items():
            setattr(translation, key, value)
        translation.total_accesses = (translation.total_accesses or 1) + 1
    else:
        translation = Translation(
            document_id=document.id,
            document_version_id=version.id,
            total_accesses=1,
            **common_fields,
        )
        db.add(translation)
        db.flush()

    db.query(ClinicalAlert).filter(ClinicalAlert.translation_id == translation.id).delete(synchronize_session=False)
    for alert in derive_alert_candidates(normalized_text or "", result_payload):
        db.add(
            ClinicalAlert(
                translation_id=translation.id,
                source_type=alert.source_type,
                severity=alert.severity,
                code=alert.code,
                title=alert.title,
                message=alert.message,
                requires_urgent_care=alert.requires_urgent_care,
            )
        )

    return translation


def load_document_asset_base64(
    db: Session,
    *,
    document_id: str,
    preferred_kind: str = "original_image",
) -> Optional[str]:
    asset = (
        db.query(DocumentAsset)
        .filter(DocumentAsset.document_id == document_id)
        .filter(DocumentAsset.kind == preferred_kind)
        .order_by(DocumentAsset.created_at.desc())
        .first()
    )
    if not asset:
        return None
    return storage_service.read_base64(asset.storage_key)
