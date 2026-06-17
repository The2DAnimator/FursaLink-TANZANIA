from django.conf import settings
from django.db import models

from apps.businesses.models import Business
from apps.core.models import TimeStampedModel


class Lead(TimeStampedModel):
    """A connection between an interested party and a business.

    The platform never sells phone numbers; a lead represents a
    permission-based introduction with an attached relevance score.
    """

    class Type(models.TextChoices):
        BUYER = "buyer", "Interested Buyer"
        SUPPLIER = "supplier", "Supplier Lead"
        PARTNERSHIP = "partnership", "Partnership Lead"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="leads")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_leads",
    )
    type = models.CharField(max_length=12, choices=Type.choices, default=Type.BUYER, db_index=True)
    contact_name = models.CharField(max_length=160, blank=True)
    message = models.TextField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.NEW, db_index=True
    )
    score = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("-score", "-created_at")
        indexes = [models.Index(fields=["business", "status"])]

    def __str__(self):
        return f"{self.get_type_display()} lead for {self.business.name} (score {self.score})"

    def compute_score(self):
        """Simple transparent lead score (0-100).

        Combines relevance (industry match), recency/activity and lead type.
        Replaceable by the ML model in apps.matching.
        """
        score = 30
        if self.industry and self.business.category:
            if self.industry.lower() in (self.business.category.name or "").lower():
                score += 30
        if self.message:
            score += min(len(self.message) // 20, 20)
        if self.type == self.Type.PARTNERSHIP:
            score += 10
        return min(score, 100)
