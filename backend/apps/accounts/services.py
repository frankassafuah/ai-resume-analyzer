"""Account services — business logic for auth and profile management.

Views stay thin and delegate here. Services never touch DRF request/response
objects; they take plain data and return model instances or raise domain errors.
"""
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.repositories import UserRepository
from apps.common.exceptions import ValidationError
from apps.common.services import BaseService

User = get_user_model()


class AccountService(BaseService):
    def __init__(self, users: UserRepository | None = None) -> None:
        super().__init__()
        self.users = users or UserRepository()

    def register(self, *, email: str, password: str,
                 first_name: str = "", last_name: str = ""):
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.logger.info("Registered user %s", user.id)
        return user

    def update_profile(self, user, data: dict[str, Any]):
        for field, value in data.items():
            setattr(user, field, value)
        user.save(update_fields=[*data.keys(), "updated_at"])
        return user

    # --- password reset ---------------------------------------------------
    def initiate_password_reset(self, *, email: str) -> None:
        """Email a reset link. Never reveals whether the email exists
        (prevents account enumeration) — always returns normally."""
        user = self.users.get_by_email(email)
        if user is None or not user.is_active:
            self.logger.info("Password reset requested for unknown email")
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

        send_mail(
            subject="Reset your password",
            message=(
                "Use the link below to reset your password:\n\n"
                f"{reset_url}\n\nIf you didn't request this, ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        self.logger.info("Password reset email sent to user %s", user.id)

    def reset_password(self, *, uid: str, token: str, password: str) -> None:
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = self.users.get_or_none(pk=pk)
        except (ValueError, TypeError, OverflowError):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            raise ValidationError("Invalid or expired password reset link.")

        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
        self.logger.info("Password reset completed for user %s", user.id)
