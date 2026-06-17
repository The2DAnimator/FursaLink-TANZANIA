"""Test settings: fast, isolated, no external services."""
from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Use an in-memory SQLite database for fast, dependency-free tests/CI.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
CELERY_TASK_STORE_EAGER_RESULT = False

# Disable manifest static storage so collectstatic is not required in tests.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
