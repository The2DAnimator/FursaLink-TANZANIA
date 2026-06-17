"""Development settings."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Console email backend so verification / reset flows are visible in dev.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Run Celery tasks synchronously when no worker is available.
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=False, cast=bool)  # noqa: F405
