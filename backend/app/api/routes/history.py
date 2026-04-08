"""
Rotas de historico de traducoes do usuario.
"""
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import TranslationHistory, User
from app.services.auth_service import get_current_user, get_current_user_optional
from app.services.history_service import generate_file_hash
from app.services.storage_service import secure_storage
from app.utils.datetime_utils import serialize_brazil_datetime


router = APIRouter()


class HistoryEnvelope(BaseModel):
    success: bool
    data: list[dict]
    error: Optional[str] = None


class FileDuplicateEnvelope(BaseModel):
    success: bool
    duplicate: bool
    history_item_id: Optional[str] = None
    translated_summary: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


@router.get("/image/{record_id}")
async def get_history_image(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recupera a imagem original criptografada do historico."""
    record = (
        db.query(TranslationHistory)
        .filter(TranslationHistory.id == record_id)
        .filter(TranslationHistory.user_id == current_user.id)
        .first()
    )

    if not record or not record.original_image_base64:
        return Response(status_code=404, content="Imagem nao encontrada")

    if not record.original_image_base64.startswith("encrypted://"):
        # Legado ou formato invalido
        return Response(status_code=400, content="Formato de imagem nao suportado para recuperacao segura")

    filename = record.original_image_base64.replace("encrypted://", "")
    image_bytes = secure_storage.get_image(filename)

    if not image_bytes:
        return Response(status_code=404, content="Arquivo de imagem nao encontrado no storage")

    return Response(
        content=image_bytes,
        media_type=record.original_image_media_type or "image/jpeg"
    )


@router.get("/mine", response_model=HistoryEnvelope)
async def get_my_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> HistoryEnvelope:
    if not current_user:
        return HistoryEnvelope(success=False, data=[], error="Nao autenticado")

    records = (
        db.query(TranslationHistory)
        .filter(TranslationHistory.user_id == current_user.id)
        .order_by(TranslationHistory.last_accessed_at.desc(), TranslationHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    return HistoryEnvelope(
        success=True,
        data=[
            {
                "id": record.id,
                "source": record.source,
                "input_type": record.input_type,
                "document_category": record.document_category,
                "document_type": record.document_type,
                "original_text": record.original_text or record.original_excerpt,
                "original_image_base64": record.original_image_base64,
                "original_image_media_type": record.original_image_media_type,
                "original_excerpt": record.original_excerpt,
                "translated_summary": record.translated_summary,
                "result_payload": json.loads(record.result_payload),
                "total_accesses": record.total_accesses,
                "last_accessed_at": serialize_brazil_datetime(
                    record.last_accessed_at or record.created_at
                ),
                "created_at": serialize_brazil_datetime(record.created_at),
            }
            for record in records
        ],
    )


@router.post("/check-file-duplicate", response_model=FileDuplicateEnvelope)
async def check_file_duplicate(
    file: UploadFile = File(..., description="Arquivo para checagem de duplicidade"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> FileDuplicateEnvelope:
    if not current_user:
        return FileDuplicateEnvelope(success=True, duplicate=False)

    file_bytes = await file.read()
    await file.seek(0)

    if not file_bytes:
        return FileDuplicateEnvelope(success=False, duplicate=False, error="Arquivo vazio")

    file_hash = generate_file_hash(file_bytes)
    existing_history = (
        db.query(TranslationHistory)
        .filter(TranslationHistory.user_id == current_user.id)
        .filter(TranslationHistory.file_hash == file_hash)
        .order_by(TranslationHistory.last_accessed_at.desc(), TranslationHistory.created_at.desc())
        .first()
    )

    if not existing_history:
        return FileDuplicateEnvelope(success=True, duplicate=False)

    return FileDuplicateEnvelope(
        success=True,
        duplicate=True,
        history_item_id=existing_history.id,
        translated_summary=existing_history.translated_summary,
        created_at=serialize_brazil_datetime(
            existing_history.last_accessed_at or existing_history.created_at
        ),
    )
