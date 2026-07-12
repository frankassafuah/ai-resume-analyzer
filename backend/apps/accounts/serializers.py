"""Account serializers.

Input serializers validate request bodies; output serializers shape responses.
The two are kept separate so request payloads can never accept server-controlled
fields, and responses never leak sensitive ones.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# --- output ---------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (response only)."""

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "profile_image",
            "email_verified",
            "created_at",
        ]
        read_only_fields = fields


# --- registration ---------------------------------------------------------
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


# --- login (JWT) ----------------------------------------------------------
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """SimpleJWT login keyed on email (USERNAME_FIELD), returning the user too."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


# --- profile update -------------------------------------------------------
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile_image"]


# --- password reset -------------------------------------------------------
class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


# --- logout ---------------------------------------------------------------
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
