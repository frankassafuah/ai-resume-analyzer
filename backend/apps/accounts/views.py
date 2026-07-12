"""Account/auth views.

Thin controllers: validate via serializer -> call AccountService (or SimpleJWT)
-> return data. The success envelope is applied by StandardJSONRenderer; errors
by custom_exception_handler.
"""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    EmailTokenObtainPairSerializer,
    LogoutSerializer,
    PasswordForgotSerializer,
    PasswordResetSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.accounts.services import AccountService
from apps.common.exceptions import ValidationError


@extend_schema(
    tags=["auth"],
    request=RegisterSerializer,
    responses={201: UserSerializer},
    summary="Register a new user",
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AccountService().register(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["auth"], summary="Obtain JWT access & refresh tokens")
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema(tags=["auth"], summary="Refresh an access token")
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


@extend_schema(
    tags=["auth"],
    request=LogoutSerializer,
    responses={205: OpenApiResponse(description="Refresh token blacklisted")},
    summary="Log out (blacklist refresh token)",
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError as exc:
            raise ValidationError("Invalid or expired refresh token.") from exc
        return Response(status=status.HTTP_205_RESET_CONTENT)


@extend_schema(
    tags=["auth"],
    request=PasswordForgotSerializer,
    responses={200: OpenApiResponse(description="Reset email sent if account exists")},
    summary="Request a password-reset email",
)
class PasswordForgotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordForgotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AccountService().initiate_password_reset(**serializer.validated_data)
        # Always 200 regardless of whether the email exists (no enumeration).
        return Response(
            {"detail": "If an account exists, a reset link has been sent."}
        )


@extend_schema(
    tags=["auth"],
    request=PasswordResetSerializer,
    responses={200: OpenApiResponse(description="Password updated")},
    summary="Reset a password using the emailed token",
)
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AccountService().reset_password(**serializer.validated_data)
        return Response({"detail": "Password has been reset."})


@extend_schema(tags=["profile"], summary="Retrieve or update the current user")
class ProfileView(RetrieveUpdateAPIView):
    """GET returns the current user; PATCH/PUT updates the profile."""

    permission_classes = [IsAuthenticated]
    # DRF defaults (JSON + Form + MultiPart) handle profile_image uploads.

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        return ProfileUpdateSerializer if self.request.method in ("PUT", "PATCH") \
            else UserSerializer

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = AccountService().update_profile(
            self.request.user, serializer.validated_data
        )
        return Response(UserSerializer(user).data)
