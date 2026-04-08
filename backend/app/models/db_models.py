"""
Modelos SQLAlchemy para persistencia de dados.
"""
import enum
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import brazil_now


def generate_uuid():
    return str(uuid.uuid4())


class CondicaoCategoria(str, enum.Enum):
    CARDIOVASCULAR = "cardiovascular"
    RESPIRATORIO = "respiratorio"
    NEUROLOGICO = "neurologico"
    ONCOLOGICO = "oncologico"
    ORTOPEDICO = "ortopedico"
    ENDOCRINOLOGICO = "endocrinologico"
    OUTRO = "outro"


class FaixaEtaria(str, enum.Enum):
    CRIANCA = "0-17"
    JOVEM = "18-30"
    ADULTO = "31-45"
    MEIA_IDADE = "46-60"
    IDOSO = "60+"
    NAO_INFORMADO = "nao_informado"


class UserRole(str, enum.Enum):
    USER = "user"
    SPECIALIST = "specialist"
    ADMIN = "admin"


class SpecialistVerificationStatus(str, enum.Enum):
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class UserProfileType(str, enum.Enum):
    PATIENT = "patient"
    CAREGIVER = "caregiver"
    STUDENT = "student"
    HEALTH_PROFESSIONAL = "health_professional"
    RESEARCHER = "researcher"
    OTHER = "other"


class User(Base):
    """Usuario autenticado da plataforma."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.USER.value, index=True)
    profile_type = Column(String(30), nullable=False, default=UserProfileType.PATIENT.value)
    age = Column(Integer, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    institution = Column(String(255), nullable=True)
    specialty = Column(String(120), nullable=True)
    professional_registry_type = Column(String(20), nullable=True)
    professional_registry_number = Column(String(30), nullable=True)
    professional_registry_state = Column(String(2), nullable=True)
    specialist_verification_status = Column(
        String(20),
        nullable=False,
        default=SpecialistVerificationStatus.NOT_APPLICABLE.value,
        index=True,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)
    updated_at = Column(DateTime, default=brazil_now, onupdate=brazil_now, nullable=False)

    consents = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")
    translation_history = relationship("TranslationHistory", back_populates="user", cascade="all, delete-orphan")


class UserConsent(Base):
    """Consentimentos versionados do usuario."""
    __tablename__ = "user_consents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    terms_accepted = Column(Boolean, nullable=False, default=False)
    privacy_accepted = Column(Boolean, nullable=False, default=False)
    research_consent = Column(Boolean, nullable=False, default=False)
    contact_consent = Column(Boolean, nullable=False, default=False)
    consent_version = Column(String(20), nullable=False, default="v1")
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    user = relationship("User", back_populates="consents")


class AuthSession(Base):
    """Sessao autenticada por token opaco."""
    __tablename__ = "auth_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=brazil_now, nullable=False)
    last_seen_at = Column(DateTime, default=brazil_now, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")


class TranslationHistory(Base):
    """Historico de traducoes do usuario."""
    __tablename__ = "translation_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    document_hash = Column(String(64), nullable=True, index=True)
    file_hash = Column(String(64), nullable=True, index=True)
    source = Column(String(30), nullable=False, index=True)
    input_type = Column(String(20), nullable=False)
    document_category = Column(String(30), nullable=True, index=True)
    document_type = Column(String(50), nullable=True)
    original_text = Column(Text, nullable=True)
    original_image_base64 = Column(Text, nullable=True)
    original_image_media_type = Column(String(50), nullable=True)
    original_excerpt = Column(Text, nullable=True)
    translated_summary = Column(Text, nullable=False)
    result_payload = Column(Text, nullable=False)
    total_accesses = Column(Integer, nullable=False, default=1)
    last_accessed_at = Column(DateTime, default=brazil_now, nullable=False)
    created_at = Column(DateTime, default=brazil_now, nullable=False)

    user = relationship("User", back_populates="translation_history")


class StatusRevisao(str, enum.Enum):
    NAO_SOLICITADA = "nao_solicitada"
    PENDENTE = "pendente"
    EM_REVISAO = "em_revisao"
    CONCLUIDA = "concluida"


class Traducao(Base):
    """Armazena traducoes epidemiologicas realizadas."""
    __tablename__ = "traducoes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    documento_hash = Column(String(64), nullable=True, index=True)
    texto_original = Column(Text, nullable=False)
    texto_traduzido = Column(Text, nullable=False)
    resultado_json = Column(Text, nullable=True)
    glossario_json = Column(Text, nullable=True)
    condicao_categoria = Column(String(50), nullable=True)
    solicitar_revisao = Column(Boolean, nullable=False, default=False)
    status_revisao = Column(String(20), nullable=False, default=StatusRevisao.NAO_SOLICITADA.value, index=True)
    ultimo_acesso_em = Column(DateTime, default=brazil_now, nullable=False)
    total_acessos = Column(Integer, nullable=False, default=1)
    cache_hits = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime, default=brazil_now)

    user = relationship("User", foreign_keys=[user_id])
    metadado = relationship("EpidemiologiaMetadado", back_populates="traducao", uselist=False)
    revisao = relationship("RevisaoEspecialista", back_populates="traducao", uselist=False)


class EpidemiologiaMetadado(Base):
    """
    Metadados epidemiologicos anonimizados.
    Compliance LGPD: apenas dados agregados, sem PII.
    """
    __tablename__ = "epidemio_metadados"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    traducao_id = Column(String(36), ForeignKey("traducoes.id"), nullable=False, unique=True)
    municipio = Column(String(100), nullable=False, index=True)
    estado = Column(String(2), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    condicao_categoria = Column(String(50), nullable=False, index=True)
    faixa_etaria = Column(String(20), nullable=False)
    mes_ano = Column(Date, nullable=False, index=True)
    criado_em = Column(DateTime, default=brazil_now)

    traducao = relationship("Traducao", back_populates="metadado")


class RevisaoEspecialista(Base):
    """
    Revisao tecnica feita por especialista verificado.
    Captura qualidade da traducao, fidelidade ao laudo e risco clinico.
    """
    __tablename__ = "revisoes_especialista"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    traducao_id = Column(String(36), ForeignKey("traducoes.id"), nullable=False, unique=True, index=True)
    especialista_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Notas de 1 a 5
    nota_fidelidade = Column(Float, nullable=False)  # Preservacao dos achados clinicos
    nota_clareza = Column(Float, nullable=False)     # Clareza da linguagem para paciente
    nota_risco = Column(Float, nullable=False)       # Risco de omissao/exagero/erro (5=baixo risco, 1=alto risco)
    nota_geral = Column(Float, nullable=False)       # Media calculada

    # Feedback textual
    comentario_tecnico = Column(Text, nullable=True)
    sugestao_correcao = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=brazil_now)

    traducao = relationship("Traducao", back_populates="revisao")
    especialista = relationship("User", foreign_keys=[especialista_id])
