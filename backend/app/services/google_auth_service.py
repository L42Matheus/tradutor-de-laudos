"""
Serviço de autenticação via Google OAuth2.
"""
import logging
from typing import Optional, Tuple
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.db_models import User, UserRole, UserProfileType
from app.services.auth_service import hash_password, create_auth_session

settings = get_settings()
logger = logging.getLogger(__name__)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

class GoogleAuthService:
    """Gerencia a integração com Google Social Login."""

    @staticmethod
    async def get_login_url(request: Request, redirect_uri: str):
        """Gera a URL de redirecionamento para o Google."""
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @staticmethod
    async def process_callback(request: Request, db: Session) -> Tuple[Optional[User], str]:
        """
        Processa o retorno do Google, cria ou vincula o usuário.
        Retorna (User, Token).
        """
        try:
            token_data = await oauth.google.authorize_access_token(request)
            user_info = token_data.get('userinfo')
            
            if not user_info:
                logger.error("Userinfo não encontrado no token do Google")
                return None, ""

            email = user_info.get('email')
            google_id = user_info.get('sub')
            full_name = user_info.get('name')

            if not email or not google_id:
                logger.error(f"Dados insuficientes do Google: email={email}, id={google_id}")
                return None, ""

            # 1. Tenta encontrar por google_id
            user = db.query(User).filter(User.google_id == google_id).first()
            
            # 2. Se não achou, tenta encontrar por email (para vincular conta existente)
            if not user:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    user.google_id = google_id
                    user.social_provider = 'google'
                    logger.info(f"Conta existente vinculada ao Google: {email}")
                else:
                    # 3. Se não existe, cria um novo usuário
                    logger.info(f"Criando novo usuário via Google: {email}")
                    user = User(
                        full_name=full_name or email.split('@')[0],
                        email=email,
                        google_id=google_id,
                        social_provider='google',
                        password_hash=hash_password(f"social_{google_id}"), 
                        role=UserRole.USER.value,
                        profile_type=UserProfileType.PATIENT.value,
                        is_active=True
                    )
                    db.add(user)
            
            db.flush()
            token = create_auth_session(db, user)
            db.commit()
            db.refresh(user)
            
            return user, token

        except Exception as e:
            logger.error(f"Erro crítico no callback do Google: {str(e)}", exc_info=True)
            return None, ""

google_auth_service = GoogleAuthService()
