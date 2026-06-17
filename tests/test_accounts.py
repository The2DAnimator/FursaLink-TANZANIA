import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import EmailVerificationToken, PasswordResetToken

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_register_creates_unverified_user(api):
    resp = api.post(
        "/api/v1/auth/register/",
        {
            "email": "new@example.com",
            "password": "Str0ngPass!2024",
            "password_confirm": "Str0ngPass!2024",
            "role": "buyer",
        },
        format="json",
    )
    assert resp.status_code == 201
    user = User.objects.get(email="new@example.com")
    assert user.is_verified is False
    assert EmailVerificationToken.objects.filter(user=user).exists()


def test_cannot_register_as_super_admin(api):
    resp = api.post(
        "/api/v1/auth/register/",
        {
            "email": "evil@example.com",
            "password": "Str0ngPass!2024",
            "password_confirm": "Str0ngPass!2024",
            "role": "super_admin",
        },
        format="json",
    )
    assert resp.status_code == 400


def test_password_mismatch_rejected(api):
    resp = api.post(
        "/api/v1/auth/register/",
        {
            "email": "x@example.com",
            "password": "Str0ngPass!2024",
            "password_confirm": "different",
            "role": "buyer",
        },
        format="json",
    )
    assert resp.status_code == 400


def test_login_returns_tokens_and_user(api, make_user):
    make_user(email="login@example.com")
    resp = api.post(
        "/api/v1/auth/login/",
        {"email": "login@example.com", "password": "password123"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data and "refresh" in resp.data
    assert resp.data["user"]["email"] == "login@example.com"


def test_email_verification_flow(api, make_user):
    user = make_user(email="verify@example.com")
    user.is_verified = False
    user.save()
    token = EmailVerificationToken.issue(user)
    resp = api.post("/api/v1/auth/verify-email/", {"token": token.token}, format="json")
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.is_verified is True


def test_password_reset_flow(api, make_user):
    user = make_user(email="reset@example.com")
    token = PasswordResetToken.issue(user)
    resp = api.post(
        "/api/v1/auth/password-reset/confirm/",
        {"token": token.token, "new_password": "BrandNew!2024"},
        format="json",
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.check_password("BrandNew!2024")


def test_me_requires_auth(api):
    assert api.get("/api/v1/me/").status_code == 401
