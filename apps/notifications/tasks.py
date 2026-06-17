"""Async notification dispatch tasks."""
from celery import shared_task

from apps.notifications.models import Notification
from apps.notifications.services import notify


@shared_task
def dispatch_notification(user_id, title, body="", category=Notification.Category.SYSTEM, channels=None):
    from apps.accounts.models import User

    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    notify(user, title=title, body=body, category=category, channels=set(channels or []))


@shared_task
def broadcast_alert(user_ids, title, body, category):
    from apps.accounts.models import User

    for user in User.objects.filter(id__in=user_ids):
        notify(user, title=title, body=body, category=category, channels={"email"})
