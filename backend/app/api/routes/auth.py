"""
Rotas de autenticacao, cadastro e consentimento.
"""
import re
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Header, Request, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import (
    SpecialistVerificationStatus,
    User,
    UserConsent,
    UserProfileType,
    UserRole,
)
from app.services.auth_service import (
    build_user_payload,
    create_auth_session,
    get_current_user_optional,
    get_user_by_email,
    hash_password,
    revoke_session,
    verify_password,
)
from app.config import get_settings

settings = get_settings()


router = APIRouter()


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=150)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    account_type: str = Field(default="patient")
    profile_type: str = Field(default=UserProfileType.PATIENT.value)
    age: int = Field(..., ge=0, le=120)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    institution: Optional[str] = Field(default=None, max_length=255)
    specialty: Optional[str] = Field(default=None, max_length=120)
    professional_registry_type: Optional[str] = Field(default=None, max_length=20)
    professional_registry_number: Optional[str] = Field(default=None, max_length=30)
    professional_registry_state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    terms_accepted: bool
    privacy_accepted: bool
    research_consent: bool = False
    contact_consent: bool = False

    @field_validator(
        "institution",
        "specialty",
        "professional_registry_type",
        "professional_registry_number",
        "professional_registry_state",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @field_validator("city", "state", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Senha deve conter pelo menos uma letra maiuscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("Senha deve conter pelo menos uma letra minuscula")
        if not re.search(r"\d", value):
            raise ValueError("Senha deve conter pelo menos um numero")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", value):
            raise ValueError("Senha deve conter pelo menos um caractere especial")
        return value


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class AuthEnvelope(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


def _build_auth_response(user: User, token: str) -> dict:
    return {
        "token": token,
        "user": build_user_payload(user),
    }


def _is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or "") is not None


def _normalizar_registro_numero(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    cleaned = re.sub(r"\D", "", value)
    return cleaned or None


def _should_use_secure_cookie(request: Request) -> bool:
    """Determina se deve usar cookie seguro baseado no ambiente."""
    try:
        host = (request.headers.get("host") or "").lower()
        forwarded_proto = (request.headers.get("x-forwarded-proto") or "").lower()

        # Tenta obter o scheme da URL
        scheme = ""
        if forwarded_proto:
            scheme = forwarded_proto
        elif request.url and hasattr(request.url, 'scheme'):
            scheme = (request.url.scheme or "").lower()

        # Localhost sempre sem secure
        if host.startswith("localhost") or host.startswith("127.0.0.1"):
            return False

        # HTTPS em produção usa secure
        return scheme == "https" and not settings.debug
    except Exception:
        # Em caso de erro, retorna False (mais permissivo)
        return False


def _set_auth_cookie(response: Response, request: Request, token: str):
    """Configura o cookie HttpOnly de autenticacao."""
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,  # 30 dias
        expires=30 * 24 * 60 * 60,
        samesite="lax",
        secure=_should_use_secure_cookie(request),
    )


@router.post("/register", response_model=AuthEnvelope)
async def register(
    request: RegisterRequest, 
    response: Response,
    http_request: Request,
    db: Session = Depends(get_db)
) -> AuthEnvelope:
    if not request.terms_accepted or not request.privacy_accepted:
        return AuthEnvelope(success=False, error="Termos e privacidade precisam ser aceitos")

    if not _is_valid_email(request.email):
        return AuthEnvelope(success=False, error="Email invalido")

    if request.account_type not in {"patient", "specialist"}:
        return AuthEnvelope(success=False, error="Tipo de conta invalido")

    if request.account_type == "patient" and request.profile_type not in {
        item.value for item in UserProfileType
    }:
        return AuthEnvelope(success=False, error="Perfil informado invalido")

    if request.account_type == "specialist":
        if not request.specialty or len(request.specialty.strip()) < 3:
            return AuthEnvelope(success=False, error="Especialidade obrigatoria para especialista")

        valid_registry_types = {"CRM", "COREN", "CRO", "CRP", "CRF", "CREFITO", "CRN", "CRBM"}
        if request.professional_registry_type not in valid_registry_types:
            return AuthEnvelope(success=False, error="Registro profissional invalido")

        professional_registry_number = _normalizar_registro_numero(
            request.professional_registry_number
        )
        if not professional_registry_number:
            return AuthEnvelope(success=False, error="Numero do CRM obrigatorio")

        if not request.professional_registry_state:
            return AuthEnvelope(success=False, error="UF do CRM obrigatoria")
    else:
        professional_registry_number = None

    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        return AuthEnvelope(success=False, error="Ja existe uma conta com este email")

    role = UserRole.SPECIALIST.value if request.account_type == "specialist" else UserRole.USER.value
    profile_type = (
        UserProfileType.HEALTH_PROFESSIONAL.value
        if request.account_type == "specialist"
        else request.profile_type
    )
    verification_status = (
        SpecialistVerificationStatus.PENDING.value
        if request.account_type == "specialist"
        else SpecialistVerificationStatus.NOT_APPLICABLE.value
    )

    user = User(
        full_name=request.full_name.strip(),
        email=request.email.lower().strip(),
        password_hash=hash_password(request.password),
        role=role,
        profile_type=profile_type,
        age=request.age,
        city=request.city.strip(),
        state=request.state.upper().strip(),
        institution=request.institution.strip() if request.institution else None,
        specialty=request.specialty.strip() if request.specialty else None,
        professional_registry_type=request.professional_registry_type,
        professional_registry_number=professional_registry_number,
        professional_registry_state=request.professional_registry_state.upper().strip()
        if request.professional_registry_state
        else None,
        specialist_verification_status=verification_status,
    )
    db.add(user)
    db.flush()

    consent = UserConsent(
        user_id=user.id,
        terms_accepted=request.terms_accepted,
        privacy_accepted=request.privacy_accepted,
        research_consent=request.research_consent,
        contact_consent=request.contact_consent,
    )
    db.add(consent)

    token = create_auth_session(db, user)
    db.commit()
    db.refresh(user)

    _set_auth_cookie(response, http_request, token)
    return AuthEnvelope(success=True, data=_build_auth_response(user, token))


@router.post("/login", response_model=AuthEnvelope)
async def login(
    request: LoginRequest, 
    response: Response,
    http_request: Request,
    db: Session = Depends(get_db)
) -> AuthEnvelope:
    if not _is_valid_email(request.email):
        return AuthEnvelope(success=False, error="Email invalido")

    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.password_hash):
        return AuthEnvelope(success=False, error="Email ou senha invalidos")

    if not user.is_active:
        return AuthEnvelope(success=False, error="Conta inativa")

    token = create_auth_session(db, user)
    db.commit()
    db.refresh(user)

    _set_auth_cookie(response, http_request, token)
    return AuthEnvelope(success=True, data=_build_auth_response(user, token))


@router.get("/me", response_model=AuthEnvelope)
async def me(current_user: Optional[User] = Depends(get_current_user_optional)) -> AuthEnvelope:
    if not current_user:
        return AuthEnvelope(success=False, error="Nao autenticado")

    return AuthEnvelope(success=True, data={"user": build_user_payload(current_user)})


@router.post("/logout", response_model=AuthEnvelope)
async def logout(
    response: Response,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    auth_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> AuthEnvelope:
    # Prioridade: Cookie (Web) > Header Bearer (Mobile/Legacy)
    token_to_revoke = None

    if auth_token:
        token_to_revoke = auth_token
    elif authorization and authorization.lower().startswith("bearer "):
        token_to_revoke = authorization.split(" ", 1)[1].strip()

    if token_to_revoke:
        revoke_session(db, token_to_revoke)
        db.commit()

    # Limpar Cookie
    response.delete_cookie(key="auth_token", samesite="lax", httponly=True)

    return AuthEnvelope(success=True, data={"logged_out": True})
