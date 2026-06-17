"""High-level notification dispatch that fans out to the right channel.

Persists an in-app Notification record and, depending on the user's
preferences, dispatches via email / SMS / WhatsApp using apps.integrations.
"""
from apps.integrations.email import EmailService
from apps.integrations.sms import SMSService
from apps.integrations.whatsapp import WhatsAppService
from apps.notifications.models import Notification, NotificationPreference


def _prefs(user) -> NotificationPreference:
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    return prefs


def notify(user, *, title, body="", category=Notification.Category.SYSTEM, channels=None):
    """Create an in-app notification and optionally push to other channels."""
    Notification.objects.create(
        user=user, title=title, body=body, category=category,
        channel=Notification.Channel.IN_APP, sent=True, is_read=False,
    )
    prefs = _prefs(user)
    channels = channels or set()

    if "email" in channels and prefs.email_enabled and user.email:
        EmailService().send(to=user.email, subject=title, body=body)
    if "sms" in channels and prefs.sms_enabled and user.phone:
        SMSService().send(to=user.phone, body=f"{title}: {body}")
    if "whatsapp" in channels and prefs.whatsapp_enabled and user.phone:
        WhatsAppService().send(to=user.phone, body=f"{title}: {body}")
