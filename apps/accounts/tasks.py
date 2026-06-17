"""Async account-related tasks (email verification, password reset)."""
from celery import shared_task
from django.conf import settings

from apps.integrations.email import EmailService


@shared_task
def send_verification_email(user_id, token):
    from apps.accounts.models import User

    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    EmailService().send(
        to=user.email,
        subject="Verify your FursaLink Tanzania account",
        body=(
            f"Karibu {user.full_name}!\n\n"
            f"Please verify your email by visiting:\n{link}\n\n"
            "If you did not create this account, you can ignore this email."
        ),
    )


@shared_task
def send_password_reset_email(user_id, token):
    from apps.accounts.models import User

    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    EmailService().send(
        to=user.email,
        subject="Reset your FursaLink Tanzania password",
        body=(
            f"Hello {user.full_name},\n\n"
            f"Reset your password using this link (valid for 2 hours):\n{link}\n\n"
            "If you did not request this, please ignore this email."
        ),
    )
