"""Production settings."""
from .base import *  # noqa: F401,F403

DEBUG = False

# Security hardening
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
CSRF_TRUSTED_ORIGINS = config(  # noqa: F405
    "CSRF_TRUSTED_ORIGINS", default="https://fursalink.co.tz", cast=Csv()  # noqa: F405
)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.sendgrid.net")  # noqa: F405
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="apikey")  # noqa: F405
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")  # noqa: F405
