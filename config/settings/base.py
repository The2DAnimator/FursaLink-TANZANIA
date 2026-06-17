"""
Base Django settings for FursaLink Tanzania.

Settings are split into base / dev / prod / test modules. Select one via the
DJANGO_SETTINGS_MODULE environment variable, e.g.:

    DJANGO_SETTINGS_MODULE=config.settings.dev

Configuration values are read from the environment (12-factor) using
python-decouple, so the same image runs in every environment.
"""
from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "django_celery_beat",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.businesses",
    "apps.products",
    "apps.opportunities",
    "apps.tenders",
    "apps.jobs",
    "apps.marketprices",
    "apps.matching",
    "apps.leads",
    "apps.advertising",
    "apps.notifications",
    "apps.analytics",
    "apps.subscriptions",
    "apps.integrations",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.parse(
        config(
            "DATABASE_URL",
            default="postgres://fursalink:fursalink@localhost:5432/fursalink",
        ),
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("DJANGO_TIME_ZONE", default="Africa/Dar_es_Salaam")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("THROTTLE_ANON", default="60/min"),
        "user": config("THROTTLE_USER", default="1000/min"),
        "otp": config("THROTTLE_OTP", default="5/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=config("JWT_ACCESS_MINUTES", default=60, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("JWT_REFRESH_DAYS", default=7, cast=int)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FursaLink Tanzania API",
    "DESCRIPTION": (
        "Business opportunity and market intelligence platform for Tanzania. "
        "Connects businesses, buyers, sellers, job seekers, and investors."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1",
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    "collect-external-tenders": {
        "task": "apps.tenders.tasks.collect_external_tenders",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    "collect-external-jobs": {
        "task": "apps.jobs.tasks.collect_external_jobs",
        "schedule": 60 * 60 * 6,
    },
    "expire-advertisements": {
        "task": "apps.core.tasks.expire_advertisements",
        "schedule": 60 * 60,  # hourly
    },
    "expire-subscriptions": {
        "task": "apps.core.tasks.expire_subscriptions",
        "schedule": 60 * 60,
    },
    "purge-old-audit-logs": {
        "task": "apps.core.tasks.purge_old_audit_logs",
        "schedule": 60 * 60 * 24,  # daily
    },
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:8000,http://127.0.0.1:8000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@fursalink.co.tz")
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:8000")

# ---------------------------------------------------------------------------
# Third-party integration credentials (used by apps.integrations).
# When a credential is blank the related service runs in MOCK mode so the
# platform stays fully functional in development and CI.
# ---------------------------------------------------------------------------
INTEGRATIONS = {
    "GOOGLE_MAPS_API_KEY": config("GOOGLE_MAPS_API_KEY", default=""),
    "SENDGRID_API_KEY": config("SENDGRID_API_KEY", default=""),
    "TWILIO_ACCOUNT_SID": config("TWILIO_ACCOUNT_SID", default=""),
    "TWILIO_AUTH_TOKEN": config("TWILIO_AUTH_TOKEN", default=""),
    "TWILIO_FROM_NUMBER": config("TWILIO_FROM_NUMBER", default=""),
    "WHATSAPP_API_TOKEN": config("WHATSAPP_API_TOKEN", default=""),
    "WHATSAPP_PHONE_ID": config("WHATSAPP_PHONE_ID", default=""),
    "STRIPE_SECRET_KEY": config("STRIPE_SECRET_KEY", default=""),
    "STRIPE_WEBHOOK_SECRET": config("STRIPE_WEBHOOK_SECRET", default=""),
    "MPESA_CONSUMER_KEY": config("MPESA_CONSUMER_KEY", default=""),
    "MPESA_CONSUMER_SECRET": config("MPESA_CONSUMER_SECRET", default=""),
    "AIRTEL_CLIENT_ID": config("AIRTEL_CLIENT_ID", default=""),
    "AIRTEL_CLIENT_SECRET": config("AIRTEL_CLIENT_SECRET", default=""),
    "TIGO_API_KEY": config("TIGO_API_KEY", default=""),
}

# External data feeds for tenders / jobs collectors.
EXTERNAL_FEEDS = {
    "TENDERS_FEED_URL": config("TENDERS_FEED_URL", default=""),
    "JOBS_FEED_URL": config("JOBS_FEED_URL", default=""),
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": config("LOG_LEVEL", default="INFO")},
}
