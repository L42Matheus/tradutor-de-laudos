"""
Servicos de historico de traducao.
"""
import hashlib
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.db_models import TranslationHistory, User
from app.utils.datetime_utils import brazil_now


def _safe_excerpt(text: Optional[str], limit: int = 500) -> Optional[str]:
    if not text:
        return None
    text = text.strip()
    return text[:limit] if text else None


def _generate_document_hash(
    input_type: str,
    original_text: Optional[str],
    original_image_base64: Optional[str],
) -> Optional[str]:
    if input_type == "image" and original_image_base64:
        return hashlib.sha256(original_image_base64.encode("utf-8")).hexdigest()

    if original_text and original_text.strip():
        normalized_text = " ".join(original_text.split()).strip().lower()
        return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

    return None


def generate_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def register_translation_history(
    db: Session,
    user: Optional[User],
    source: str,
    input_type: str,
    document_category: Optional[str],
    document_type: Optional[str],
    original_text: Optional[str],
    result_payload: dict,
    original_image_base64: Optional[str] = None,
    original_image_media_type: Optional[str] = None,
    file_hash: Optional[str] = None,
) -> None:
    if not user:
        return

    normalized_text = original_text.strip() if original_text and original_text.strip() else None
    translated_summary = (
        result_payload.get("resumo")
        or result_payload.get("texto_traduzido")
        or "Sem resumo disponivel"
    )
    document_hash = _generate_document_hash(input_type, normalized_text, original_image_base64)
    now = brazil_now()

    existing_history = None
    if file_hash:
        existing_history = (
            db.query(TranslationHistory)
            .filter(TranslationHistory.user_id == user.id)
            .filter(TranslationHistory.file_hash == file_hash)
            .first()
        )

    if document_hash:
        existing_history = existing_history or (
            db.query(TranslationHistory)
            .filter(TranslationHistory.user_id == user.id)
            .filter(TranslationHistory.document_hash == document_hash)
            .first()
        )

    if existing_history:
        existing_history.source = source
        existing_history.input_type = input_type
        existing_history.document_category = document_category
        existing_history.document_type = document_type
        existing_history.original_text = existing_history.original_text or normalized_text
        existing_history.original_image_base64 = (
            existing_history.original_image_base64 or original_image_base64
        )
        existing_history.original_image_media_type = (
            existing_history.original_image_media_type or original_image_media_type
        )
        existing_history.original_excerpt = existing_history.original_excerpt or _safe_excerpt(normalized_text)
        existing_history.translated_summary = translated_summary
        existing_history.result_payload = json.dumps(result_payload, ensure_ascii=True)
        existing_history.total_accesses = (existing_history.total_accesses or 1) + 1
        existing_history.last_accessed_at = now
        return

    history = TranslationHistory(
        user_id=user.id,
        document_hash=document_hash,
        file_hash=file_hash,
        source=source,
        input_type=input_type,
        document_category=document_category,
        document_type=document_type,
        original_text=normalized_text,
        original_image_base64=original_image_base64,
        original_image_media_type=original_image_media_type,
        original_excerpt=_safe_excerpt(normalized_text),
        translated_summary=translated_summary,
        result_payload=json.dumps(result_payload, ensure_ascii=True),
        total_accesses=1,
        last_accessed_at=now,
    )
    db.add(history)
