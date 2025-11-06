import random
import string
from datetime import timedelta

from django.utils import timezone

from .models import Account, EmailVerification, User
from .serializers import UserRegistrationSerializer
from .utils import generate_verification_token, send_verification_email


class UserService:
    """Serviço para centralizar a lógica de criação de usuários"""

    @staticmethod
    def create_user_with_email(data):
        """Cria usuário com registro por email"""
        try:
            existing_user = User.objects.get(email=data.get("email"))
            if existing_user:
                return None, {
                    "error": ["Algo de errado aconteceu, tente novamente mais tarte"]
                }
        except User.DoesNotExist:
            pass

        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            UserService._create_email_account(user)
            UserService._send_verification_email(user)
            return user, None
        return None, serializer.errors

    @staticmethod
    def create_user_with_google(id_info):
        """Cria ou atualiza usuário com registro Google"""
        email = id_info["email"]
        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        try:
            user = User.objects.get(email=email)

            if user.registration_method == "email":
                return None, "email_conflict"

            return user, None

        except User.DoesNotExist:
            random_username = f"user_{UserService.generate_random_username()}"
            user = User.objects.create(
                email=email,
                username=random_username,
                first_name=first_name,
                last_name=last_name,
                registration_method="google",
            )
            user.set_unusable_password()
            user.save()
            UserService._create_google_account(user)

            return user, None

    @staticmethod
    def _create_email_account(user):
        """Cria account para email"""
        Account.objects.create(
            user=user,
            provider=Account.ProviderType.EMAIL,
            email_verified=False,
            is_primary=True,
        )

    @staticmethod
    def _create_google_account(user):
        """Cria account para Google"""
        Account.objects.create(
            user=user,
            provider=Account.ProviderType.GOOGLE,
            email_verified=True,
            is_primary=True,
        )

    @staticmethod
    def _send_verification_email(user):
        """Envia email de verificação"""
        EmailVerification.objects.filter(user=user, email=user.email).delete()

        email_verification = EmailVerification.objects.create(
            user=user,
            email=user.email,
            token=generate_verification_token(),
            expires_at=timezone.now() + timedelta(hours=24),
        )
        send_verification_email(user, email_verification.token)

    @staticmethod
    def generate_random_username(length=8):
        """
        Gera nome de usuário genérico
        """
        characters = string.ascii_lowercase + string.digits
        username = "".join(random.choice(characters) for i in range(length))
        return username
