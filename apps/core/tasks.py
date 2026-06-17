"""Periodic maintenance tasks (run by Celery beat)."""
from celery import shared_task
from django.utils import timezone


@shared_task
def expire_advertisements():
    from apps.advertising.models import Advertisement

    now = timezone.now()
    return Advertisement.objects.filter(
        status=Advertisement.Status.ACTIVE, ends_at__lt=now
    ).update(status=Advertisement.Status.EXPIRED)


@shared_task
def expire_subscriptions():
    from apps.subscriptions.models import Subscription

    now = timezone.now()
    return Subscription.objects.filter(
        status=Subscription.Status.ACTIVE, expires_at__lt=now
    ).update(status=Subscription.Status.EXPIRED)


@shared_task
def purge_old_audit_logs(days=180):
    from datetime import timedelta

    from apps.core.models import AuditLog

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    return deleted
