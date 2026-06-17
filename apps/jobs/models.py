from django.conf import settings
from django.db import models

from apps.businesses.models import Business
from apps.core.models import Category, Region, TimeStampedModel


class Job(TimeStampedModel):
    class Type(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        INTERNSHIP = "internship", "Internship"
        FREELANCE = "freelance", "Freelance"
        CONTRACT = "contract", "Contract"

    class Source(models.TextChoices):
        INTERNAL = "internal", "Internal"
        EXTERNAL = "external", "External Feed"

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
    )
    business = models.ForeignKey(
        Business, null=True, blank=True, on_delete=models.SET_NULL, related_name="jobs"
    )
    title = models.CharField(max_length=200, db_index=True)
    company = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    type = models.CharField(max_length=12, choices=Type.choices, default=Type.FULL_TIME, db_index=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="TZS")
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    deadline = models.DateField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.INTERNAL)
    external_id = models.CharField(max_length=120, blank=True, db_index=True)
    apply_url = models.URLField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["type", "is_active"]),
            models.Index(fields=["region", "category"]),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company}"


class JobApplication(TimeStampedModel):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        REVIEWING = "reviewing", "Reviewing"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    cover_letter = models.TextField(blank=True)
    cv = models.FileField(upload_to="applications/", blank=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SUBMITTED)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("job", "applicant")

    def __str__(self):
        return f"{self.applicant} -> {self.job}"
