import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def make_user(db):
    def _make(email="user@example.com", password="password123", role=User.Role.BUYER, **extra):
        return User.objects.create_user(email=email, password=password, role=role, is_verified=True, **extra)

    return _make


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser("admin@example.com", "password123")


@pytest.fixture
def auth_client(api, make_user):
    def _client(**kwargs):
        user = make_user(**kwargs)
        api.force_authenticate(user=user)
        return api, user

    return _client
