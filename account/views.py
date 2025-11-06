from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from account.services import UserService

from .models import Account, EmailVerification, PasswordResetToken, User
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    ProfilePictureSerializer,
    UserSerializer,
)
from .utils import generate_verification_token, send_password_reset_email


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user, errors = UserService.create_user_with_email(request.data)

        if user:
            return Response(
                {"detail": "Usuário criado. Verifique seu email para ativar a conta."},
                status=status.HTTP_201_CREATED,
            )

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)

            if verification.is_expired():
                return Response(
                    {"error": "Link de verificação expirado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not verification.verified_at:
                verification.verified_at = timezone.now()
                verification.save()

                Account.objects.filter(user=verification.user).update(
                    email_verified=True
                )

                return Response({"detail": "Email verificado com sucesso"})
            else:
                return Response({"detail": "Email já verificado"})

        except EmailVerification.DoesNotExist:
            return Response(
                {"error": "Token de verificação inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(APIView):
    def get(self, request):
        """Retorna perfil do usuário logado"""
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        """Atualiza perfil do usuário"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePictureView(APIView):
    def put(self, request):
        """Atualiza foto de perfil"""
        serializer = ProfilePictureSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Reenvia email de verificação"""
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            UserService._send_verification_email(user)
            return Response({"detail": "Email de verificação reenviado"})

        except User.DoesNotExist:
            return Response(
                {"error": "Usuário não encontrado"}, status=status.HTTP_400_BAD_REQUEST
            )


class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Token not provided", "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            id_info = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
            )

            user, error = UserService.create_user_with_google(id_info)

            if error == "email_conflict":
                return Response(
                    {
                        "error": [
                            "Algo de errado aconteceu, tente novamente mais tarte",
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                    "user": UserSerializer(user).data,
                    "status": True,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError:
            return Response(
                {"error": "Invalid token", "status": False},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Solicita reset de senha"""
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user = User.objects.get(email=email)
                PasswordResetToken.objects.filter(user=user).delete()

                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=generate_verification_token(),
                    expires_at=timezone.now() + timedelta(hours=1),
                )

                send_password_reset_email(user, reset_token.token)

                return Response({"detail": "Email de recuperação de senha enviado"})

            except User.DoesNotExist:
                return Response({"detail": "Email de recuperação de senha enviado"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Confirma reset de senha"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["new_password"]

            try:
                reset_token = PasswordResetToken.objects.get(token=token)

                if reset_token.is_expired():
                    return Response(
                        {"error": "Token expirado"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if reset_token.is_used():
                    return Response(
                        {"error": "Token já utilizado"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = reset_token.user
                user.set_password(new_password)
                user.save()

                reset_token.used_at = timezone.now()
                reset_token.save()

                return Response({"detail": "Senha redefinida com sucesso"})

            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"error": "Token inválido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
