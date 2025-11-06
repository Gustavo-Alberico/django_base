import secrets

from django.conf import settings
from django.core.mail import send_mail


def generate_verification_token():
    """Gera token seguro para verificação"""
    return secrets.token_urlsafe(32)

def send_verification_email(user, token):
    """Envia email de verificação"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    subject = "Verifique seu email"
    message = f"""
    Olá {user.first_name or user.username},
    
    Clique no link abaixo para verificar seu email:
    {verification_url}
    
    Este link expira em 24 horas.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def send_password_reset_email(user, token):
    """Envia email de recuperação de senha"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
    
    subject = "Recuperação de Senha"
    message = f"""
    Olá {user.first_name or user.username},
    
    Clique no link abaixo para redefinir sua senha:
    {reset_url}
    
    Este link expira em 1 hora.
    
    Se você não solicitou esta recuperação, ignore este email.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )