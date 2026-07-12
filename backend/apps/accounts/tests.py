"""Auth & profile flow tests."""
import io

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="jane@example.com",
        password="Str0ng-Passw0rd!",
        first_name="Jane",
        last_name="Doe",
    )


def auth(client: APIClient, user) -> APIClient:
    client.force_authenticate(user=user)
    return client


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (2, 2), "blue").save(buf, format="PNG")
    return buf.getvalue()


# --- registration ---------------------------------------------------------
def test_register_creates_user(client):
    resp = client.post(reverse("v1:accounts:register"), {
        "email": "New@Example.com",
        "password": "Str0ng-Passw0rd!",
        "first_name": "New",
        "last_name": "User",
    }, format="json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "new@example.com"  # normalized
    user = User.objects.get(email="new@example.com")
    assert user.check_password("Str0ng-Passw0rd!")
    assert user.has_usable_password()


def test_register_rejects_duplicate_email(client, user):
    resp = client.post(reverse("v1:accounts:register"), {
        "email": user.email, "password": "Str0ng-Passw0rd!",
    }, format="json")
    assert resp.status_code == 400
    assert "email" in resp.json()["error"]["details"]


def test_register_rejects_weak_password(client):
    resp = client.post(reverse("v1:accounts:register"), {
        "email": "weak@example.com", "password": "123",
    }, format="json")
    assert resp.status_code == 400
    assert "password" in resp.json()["error"]["details"]


# --- login / refresh / logout --------------------------------------------
def test_login_returns_tokens_and_user(client, user):
    resp = client.post(reverse("v1:accounts:login"), {
        "email": user.email, "password": "Str0ng-Passw0rd!",
    }, format="json")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["access"] and data["refresh"]
    assert data["user"]["email"] == user.email


def test_login_wrong_password_fails(client, user):
    resp = client.post(reverse("v1:accounts:login"), {
        "email": user.email, "password": "wrong",
    }, format="json")
    assert resp.status_code == 401


def test_refresh_issues_new_access(client, user):
    login = client.post(reverse("v1:accounts:login"), {
        "email": user.email, "password": "Str0ng-Passw0rd!",
    }, format="json").json()["data"]
    resp = client.post(reverse("v1:accounts:refresh"),
                       {"refresh": login["refresh"]}, format="json")
    assert resp.status_code == 200
    assert resp.json()["data"]["access"]


def test_logout_blacklists_refresh(client, user):
    login = client.post(reverse("v1:accounts:login"), {
        "email": user.email, "password": "Str0ng-Passw0rd!",
    }, format="json").json()["data"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login['access']}")
    out = client.post(reverse("v1:accounts:logout"),
                      {"refresh": login["refresh"]}, format="json")
    assert out.status_code == 205
    # The blacklisted refresh token can no longer be used.
    again = client.post(reverse("v1:accounts:refresh"),
                        {"refresh": login["refresh"]}, format="json")
    assert again.status_code == 401


# --- profile --------------------------------------------------------------
def test_profile_requires_auth(client):
    assert client.get(reverse("v1:accounts:profile")).status_code == 401


def test_profile_returns_current_user(client, user):
    resp = auth(client, user).get(reverse("v1:accounts:profile"))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["email"] == user.email
    assert data["full_name"] == "Jane Doe"
    assert "created_at" in data


def test_profile_update_names(client, user):
    resp = auth(client, user).patch(reverse("v1:accounts:profile"),
                                    {"first_name": "Janet"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["data"]["first_name"] == "Janet"
    user.refresh_from_db()
    assert user.first_name == "Janet"


def test_profile_update_image(client, user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    from django.core.files.uploadedfile import SimpleUploadedFile
    img = SimpleUploadedFile("a.png", _png_bytes(), content_type="image/png")
    resp = auth(client, user).patch(reverse("v1:accounts:profile"),
                                    {"profile_image": img}, format="multipart")
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.profile_image.name.startswith("avatars/")


# --- password reset -------------------------------------------------------
def test_forgot_password_sends_email(client, user):
    resp = client.post(reverse("v1:accounts:password-forgot"),
                       {"email": user.email}, format="json")
    assert resp.status_code == 200
    assert len(mail.outbox) == 1
    assert user.email in mail.outbox[0].to


def test_forgot_password_unknown_email_is_silent(client):
    resp = client.post(reverse("v1:accounts:password-forgot"),
                       {"email": "nobody@example.com"}, format="json")
    assert resp.status_code == 200          # no enumeration
    assert len(mail.outbox) == 0


def test_reset_password_with_valid_token(client, user):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    resp = client.post(reverse("v1:accounts:password-reset"), {
        "uid": uid, "token": token, "password": "N3w-Passw0rd!",
    }, format="json")
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.check_password("N3w-Passw0rd!")


def test_reset_password_with_invalid_token(client, user):
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    resp = client.post(reverse("v1:accounts:password-reset"), {
        "uid": uid, "token": "bogus-token", "password": "N3w-Passw0rd!",
    }, format="json")
    assert resp.status_code == 400
