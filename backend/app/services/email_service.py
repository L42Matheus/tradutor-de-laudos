"""
Serviço de notificações e email.
Centraliza o envio de comunicações, preparado para expansão (Email, WhatsApp, Webhooks).
"""
import logging
from typing import List, Optional
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Configuração do Provedor de Email (SMTP)
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_user,
    MAIL_PASSWORD=settings.smtp_password,
    MAIL_FROM=settings.email_from,
    MAIL_PORT=settings.smtp_port,
    MAIL_SERVER=settings.smtp_server,
    MAIL_FROM_NAME=settings.app_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class NotificationService:
    """Hub de notificações do sistema."""

    @staticmethod
    async def send_email(
        subject: str, 
        recipients: List[EmailStr], 
        body: str, 
        is_html: bool = True
    ) -> bool:
        """Envia um email via SMTP."""
        if not settings.smtp_user or not settings.smtp_password:
            logger.warning("Configurações de SMTP ausentes. Pulando envio de email.")
            # Para ambiente de dev, logamos o conteúdo
            print(f"--- EMAIL SIMULADO ---\nPara: {recipients}\nAssunto: {subject}\nCorpo: {body}\n----------------------")
            return True

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=MessageType.html if is_html else MessageType.plain
        )

        fm = FastMail(mail_config)
        try:
            await fm.send_message(message)
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False

    @staticmethod
    async def send_password_reset_email(email: str, token: str):
        """Envia o link de recuperação de senha."""
        reset_link = f"{settings.frontend_url}/reset-password?token={token}"
        
        subject = f"Recuperação de Senha - {settings.app_name}"
        body = f"""
        <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <h2>Olá!</h2>
                <p>Você solicitou a redefinição de senha para sua conta no <strong>Traduz Saúde</strong>.</p>
                <p>Clique no botão abaixo para criar uma nova senha. Este link expira em 1 hora.</p>
                <div style="margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #0284c7; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                       Redefinir Minha Senha
                    </a>
                </div>
                <p>Se você não fez esta solicitação, por favor ignore este email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #777;">Equipe Traduz Saúde</p>
            </body>
        </html>
        """
        return await NotificationService.send_email(subject, [email], body)

    @staticmethod
    async def send_webhook_notification(payload: dict, webhook_url: str):
        """
        Prepara o terreno para disparos via Webhook.
        Pode ser usado para integrar com bots de WhatsApp, analytics, etc.
        """
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json=payload, timeout=5.0)
                return True
        except Exception as e:
            logger.error(f"Erro ao disparar webhook: {str(e)}")
            return False

notification_service = NotificationService()
