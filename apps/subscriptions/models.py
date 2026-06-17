from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class Plan(models.Model):
    """A subscription tier (Free / Standard / Premium)."""

    class Tier(models.TextChoices):
        FREE = "free", "Free"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    name = models.CharField(max_length=80)
    tier = models.CharField(max_length=12, choices=Tier.choices, unique=True, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="TZS")
    billing_period_days = models.PositiveSmallIntegerField(default=30)
    max_listings = models.PositiveIntegerField(default=5)
    has_analytics = models.BooleanField(default=False)
    has_lead_generation = models.BooleanField(default=False)
    featured_placement = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)

    class Meta:
        ordering = ("price",)

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"


class Subscription(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE, db_index=True
    )
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self):
        return f"{self.user} -> {self.plan} [{self.status}]"

    @property
    def is_active(self):
        if self.status != self.Status.ACTIVE:
            return False
        return self.expires_at is None or self.expires_at >= timezone.now()


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class Provider(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        AIRTEL = "airtel_money", "Airtel Money"
        TIGO = "tigo_pesa", "Tigo Pesa"
        STRIPE = "stripe", "Stripe"

    class Purpose(models.TextChoices):
        SUBSCRIPTION = "subscription", "Subscription"
        ADVERTISEMENT = "advertisement", "Advertisement"
        FEATURED = "featured", "Featured Listing"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    subscription = models.ForeignKey(
        Subscription, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="TZS")
    provider = models.CharField(max_length=15, choices=Provider.choices)
    purpose = models.CharField(
        max_length=15, choices=Purpose.choices, default=Purpose.SUBSCRIPTION
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    reference = models.CharField(max_length=64, unique=True, db_index=True)
    provider_ref = models.CharField(max_length=120, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self):
        return f"{self.reference} {self.amount} {self.currency} [{self.status}]"
