from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "In-App"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Category(models.TextChoices):
        JOB_ALERT = "job_alert", "Job Alert"
        PRICE_ALERT = "price_alert", "Price Alert"
        OPPORTUNITY_ALERT = "opportunity_alert", "Opportunity Alert"
        TENDER_ALERT = "tender_alert", "Tender Alert"
        LEAD = "lead", "Lead"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.SYSTEM, db_index=True
    )
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["user", "is_read"])]

    def __str__(self):
        return f"{self.title} -> {self.user}"


class NotificationPreference(models.Model):
    """Per-user opt-in for alert categories and channels."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preference"
    )
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    whatsapp_enabled = models.BooleanField(default=False)
    job_alerts = models.BooleanField(default=True)
    price_alerts = models.BooleanField(default=True)
    opportunity_alerts = models.BooleanField(default=True)
    tender_alerts = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences<{self.user.email}>"
