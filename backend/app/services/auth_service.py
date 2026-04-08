"""
Servicos de autenticacao e sessao.
"""
import hashlib
import hmac
import secrets
from datetime import timedelta
from typing import Optional

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import AuthSession, User
from app.utils.datetime_utils import brazil_now, serialize_brazil_datetime


PASSWORD_ITERATIONS = 120_000
SESSION_TTL_DAYS = 30


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        _, iterations_str, salt, password_hash = stored_hash.split("$", 3)
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations_str),
        ).hex()
        return hmac.compare_digest(computed_hash, password_hash)
    except ValueError:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_auth_session(db: Session, user: User) -> str:
    raw_token = secrets.token_urlsafe(48)
    session = AuthSession(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        expires_at=brazil_now() + timedelta(days=SESSION_TTL_DAYS),
    )
    db.add(session)
    return raw_token


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def build_user_payload(user: User) -> dict:
    latest_consent = user.consents[-1] if user.consents else None
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "account_type": "specialist" if user.role == "specialist" else "patient",
        "profile_type": user.profile_type,
        "age": user.age,
        "city": user.city,
        "state": user.state,
        "institution": user.institution,
        "specialty": user.specialty,
        "professional_registry_type": user.professional_registry_type,
        "professional_registry_number": user.professional_registry_number,
        "professional_registry_state": user.professional_registry_state,
        "specialist_verification_status": user.specialist_verification_status,
        "preferred_llm_provider": user.preferred_llm_provider or "claude",
        "preferred_llm_model": user.preferred_llm_model,
        "research_consent": latest_consent.research_consent if latest_consent else False,
        "contact_consent": latest_consent.contact_consent if latest_consent else False,
        "created_at": serialize_brazil_datetime(user.created_at),
    }


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return None

    return parts[1].strip()


def get_current_user_optional(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    auth_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    # Prioridade para o Cookie (mais seguro para Web)
    token = auth_token
    
    # Se nao houver cookie, tenta o Header (Legado/Mobile)
    if not token:
        token = _extract_bearer_token(authorization)
    
    if not token:
        return None

    token_hash = hash_token(token)
    session = (
        db.query(AuthSession)
        .filter(AuthSession.token_hash == token_hash)
        .filter(AuthSession.revoked_at.is_(None))
        .first()
    )

    if not session or session.expires_at < brazil_now():
        return None

    session.last_seen_at = brazil_now()
    return session.user if session.user and session.user.is_active else None


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    auth_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    """Retorna o usuario autenticado ou levanta HTTPException 401."""
    user = get_current_user_optional(authorization, auth_token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticacao necessaria",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def revoke_session(db: Session, token: str) -> None:
    session = (
        db.query(AuthSession)
        .filter(AuthSession.token_hash == hash_token(token))
        .filter(AuthSession.revoked_at.is_(None))
        .first()
    )
    if session:
        session.revoked_at = brazil_now()
