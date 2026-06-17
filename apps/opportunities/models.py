from django.conf import settings
from django.db import models

from apps.businesses.models import Business
from apps.core.models import Region, TimeStampedModel


class Opportunity(TimeStampedModel):
    class Type(models.TextChoices):
        SUPPLY = "supply", "Supply Request"
        BUYER = "buyer", "Buyer Request"
        INVESTMENT = "investment", "Investment Opportunity"
        PARTNERSHIP = "partnership", "Partnership Opportunity"
        DISTRIBUTION = "distribution", "Distribution Opportunity"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Approval"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="opportunities"
    )
    business = models.ForeignKey(
        Business, null=True, blank=True, on_delete=models.SET_NULL, related_name="opportunities"
    )
    type = models.CharField(max_length=15, choices=Type.choices, db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    industry = models.CharField(max_length=120, blank=True, db_index=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=200, blank=True)
    budget_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="TZS")
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "opportunities"
        indexes = [
            models.Index(fields=["type", "status"]),
            models.Index(fields=["region", "industry"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"
