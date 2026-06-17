from django.conf import settings
from django.db import models

from apps.businesses.models import Business
from apps.core.models import TimeStampedModel


class AdPlan(models.Model):
    """A purchasable advertising placement / package."""

    class Placement(models.TextChoices):
        FEATURED_LISTING = "featured_listing", "Featured Listing"
        HOMEPAGE = "homepage", "Homepage Ad"
        BANNER = "banner", "Banner Ad"
        SPONSORED_OPPORTUNITY = "sponsored_opportunity", "Sponsored Opportunity"

    name = models.CharField(max_length=120)
    placement = models.CharField(max_length=30, choices=Placement.choices, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="TZS")
    duration_days = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("placement", "price")

    def __str__(self):
        return f"{self.name} ({self.get_placement_display()})"


class Advertisement(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Payment"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        REJECTED = "rejected", "Rejected"

    advertiser = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="advertisements"
    )
    business = models.ForeignKey(
        Business, null=True, blank=True, on_delete=models.SET_NULL, related_name="advertisements"
    )
    plan = models.ForeignKey(AdPlan, on_delete=models.PROTECT, related_name="advertisements")
    title = models.CharField(max_length=160)
    image = models.ImageField(upload_to="ads/", blank=True, null=True)
    target_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status", "ends_at"])]

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"
