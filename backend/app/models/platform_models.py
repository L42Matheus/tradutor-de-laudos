"""
Modelos transacionais e analiticos da arquitetura alvo em Postgres.
Mantidos em paralelo ao schema legado durante a migracao.
"""
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import brazil_now

try:
    from pgvector.sqlalchemy import Vector
except ImportError:  # pragma: no cover - fallback para ambientes sem pgvector
    Vector = None


def generate_uuid() -> str:
    return str(uuid.uuid4())


def embedding_column_type():
    if Vector is not None:
        return Vector(1536)
    return Text


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    source_route = Column(String(50), nullable=False, index=True)
    document_category = Column(String(30), nullable=True, index=True)
    document_type = Column(String(50), nullable=True)
    input_type = Column(String(20), nullable=False)
    canonical_hash = Column(String(64), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)
    updated_at = Column(DateTime, default=brazil_now, onupdate=brazil_now, nullable=False)

    assets = relationship("DocumentAsset", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="document", cascade="all, delete-orphan")


class DocumentAsset(Base):
    __tablename__ = "document_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    kind = Column(String(30), nullable=False, index=True)
    storage_backend = Column(String(20), nullable=False, default="local")
    storage_key = Column(String(255), nullable=False, unique=True)
    media_type = Column(String(100), nullable=True)
    file_name = Column(String(255), nullable=True)
    byte_size = Column(Integer, nullable=True)
    checksum_sha256 = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    document = relationship("Document", back_populates="assets")


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_versions_document_version"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    file_hash = Column(String(64), nullable=True, index=True)
    content_hash = Column(String(64), nullable=True, index=True)
    input_type = Column(String(20), nullable=False)
    extracted_text = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    anonymized_text = Column(Text, nullable=True)
    anonymized_fields_json = Column(Text, nullable=True)
    parser_provider = Column(String(50), nullable=True)
    parser_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    document = relationship("Document", back_populates="versions")
    translations = relationship("Translation", back_populates="document_version")


class Translation(Base):
    __tablename__ = "translations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    document_version_id = Column(String(36), ForeignKey("document_versions.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    source_route = Column(String(50), nullable=False, index=True)
    legacy_source_table = Column(String(50), nullable=True, index=True)
    legacy_source_id = Column(String(36), nullable=True, index=True)
    pipeline_name = Column(String(50), nullable=False, index=True)
    pipeline_version = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)
    document_category = Column(String(30), nullable=True, index=True)
    document_type = Column(String(50), nullable=True)
    input_type = Column(String(20), nullable=False)
    summary = Column(Text, nullable=False)
    detailed = Column(Text, nullable=False)
    easy_explanation = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    glossary_json = Column(Text, nullable=True)
    model_alerts_json = Column(Text, nullable=True)
    result_payload_json = Column(Text, nullable=True)
    is_mental_health = Column(Boolean, nullable=False, default=False)
    from_cache = Column(Boolean, nullable=False, default=False)
    requires_location_confirmation = Column(Boolean, nullable=False, default=False)
    specialist_review_requested = Column(Boolean, nullable=False, default=False)
    specialist_review_status = Column(String(20), nullable=False, default="nao_solicitada", index=True)
    epidemiology_category = Column(String(50), nullable=True, index=True)
    epidemiology_age_band = Column(String(20), nullable=True)
    total_accesses = Column(Integer, nullable=False, default=1)
    last_accessed_at = Column(DateTime, default=brazil_now, nullable=False)
    created_at = Column(DateTime, default=brazil_now, nullable=False)
    updated_at = Column(DateTime, default=brazil_now, onupdate=brazil_now, nullable=False)

    document = relationship("Document", back_populates="translations")
    document_version = relationship("DocumentVersion", back_populates="translations")
    clinical_alerts = relationship("ClinicalAlert", back_populates="translation", cascade="all, delete-orphan")
    review = relationship("TranslationReview", back_populates="translation", uselist=False, cascade="all, delete-orphan")
    epidemiology_event = relationship("EpidemiologyEvent", back_populates="translation", uselist=False, cascade="all, delete-orphan")


class ClinicalAlert(Base):
    __tablename__ = "clinical_alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    translation_id = Column(String(36), ForeignKey("translations.id"), nullable=False, index=True)
    source_type = Column(String(20), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    title = Column(String(150), nullable=True)
    message = Column(Text, nullable=False)
    requires_urgent_care = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    translation = relationship("Translation", back_populates="clinical_alerts")


class TranslationReview(Base):
    __tablename__ = "translation_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    translation_id = Column(String(36), ForeignKey("translations.id"), nullable=False, unique=True, index=True)
    specialist_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    fidelity_score = Column(Float, nullable=False)
    clarity_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    technical_comment = Column(Text, nullable=True)
    correction_suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    translation = relationship("Translation", back_populates="review")


class RagSource(Base):
    __tablename__ = "rag_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_type = Column(String(30), nullable=False, index=True)
    authority = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=True)
    document_code = Column(String(100), nullable=True, index=True)
    specialty = Column(String(80), nullable=True, index=True)
    metadata_json = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)
    updated_at = Column(DateTime, default=brazil_now, onupdate=brazil_now, nullable=False)

    chunks = relationship("RagChunk", back_populates="source", cascade="all, delete-orphan")


class RagChunk(Base):
    __tablename__ = "rag_chunks"
    __table_args__ = (
        UniqueConstraint("source_id", "chunk_index", name="uq_rag_chunks_source_chunk_index"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("rag_sources.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    embedding = Column(embedding_column_type(), nullable=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    source = relationship("RagSource", back_populates="chunks")


class EpidemiologyEvent(Base):
    __tablename__ = "epidemiology_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    translation_id = Column(String(36), ForeignKey("translations.id"), nullable=False, unique=True, index=True)
    municipality = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    condition_category = Column(String(50), nullable=False, index=True)
    age_band = Column(String(20), nullable=False)
    event_month = Column(Date, nullable=False, index=True)
    location_source = Column(String(30), nullable=False, default="inferred")
    source_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    translation = relationship("Translation", back_populates="epidemiology_event")
