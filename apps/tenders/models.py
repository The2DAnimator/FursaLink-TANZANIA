from django.db import models

from apps.core.models import Region, TimeStampedModel


class Tender(TimeStampedModel):
    class Sector(models.TextChoices):
        GOVERNMENT = "government", "Government"
        NGO = "ngo", "NGO"
        PRIVATE = "private", "Private"

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual"
        EXTERNAL = "external", "External Feed"

    organization = models.CharField(max_length=200, db_index=True)
    tender_number = models.CharField(max_length=120, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sector = models.CharField(max_length=12, choices=Sector.choices, db_index=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)
    closing_date = models.DateField(null=True, blank=True, db_index=True)
    documents_url = models.URLField(blank=True)
    document = models.FileField(upload_to="tenders/", blank=True, null=True)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.MANUAL)
    external_id = models.CharField(max_length=120, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["tender_number", "organization"], name="unique_tender_per_org"
            )
        ]
        indexes = [models.Index(fields=["sector", "is_active"])]

    def __str__(self):
        return f"{self.tender_number} - {self.organization}"
