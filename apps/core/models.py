"""Shared base models and platform-wide reference data."""
import uuid

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base with created/updated timestamps and a public UUID."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class Region(models.Model):
    """A Tanzanian administrative region (e.g. Dar es Salaam, Arusha)."""

    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class District(models.Model):
    """A district belonging to a region."""

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=120)

    class Meta:
        ordering = ("name",)
        unique_together = ("region", "name")
        indexes = [models.Index(fields=["region", "name"])]

    def __str__(self):
        return f"{self.name}, {self.region.name}"


class Category(TimeStampedModel):
    """Hierarchical category shared by businesses, products and opportunities."""

    class Kind(models.TextChoices):
        BUSINESS = "business", "Business"
        PRODUCT = "product", "Product"
        OPPORTUNITY = "opportunity", "Opportunity"
        JOB = "job", "Job"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.BUSINESS, db_index=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    icon = models.CharField(max_length=60, blank=True, help_text="Bootstrap icon name")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ("kind", "name")
        indexes = [models.Index(fields=["kind", "slug"])]

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class AuditLog(models.Model):
    """Immutable record of significant user actions for security/compliance."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=120, db_index=True)
    method = models.CharField(max_length=10, blank=True)
    path = models.CharField(max_length=255, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["user", "action"])]

    def __str__(self):
        return f"{self.action} by {self.user_id} @ {self.created_at:%Y-%m-%d %H:%M}"


class SiteSetting(models.Model):
    """Singleton-ish key/value store for runtime-tunable site configuration."""

    key = models.CharField(max_length=80, unique=True)
    value = models.CharField(max_length=400, blank=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.key
