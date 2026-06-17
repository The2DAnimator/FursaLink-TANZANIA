from rest_framework import serializers

from apps.jobs.models import Job, JobApplication


class JobSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    applications_count = serializers.IntegerField(source="applications.count", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "uuid",
            "posted_by",
            "business",
            "title",
            "company",
            "category",
            "description",
            "type",
            "type_display",
            "salary_min",
            "salary_max",
            "currency",
            "region",
            "location",
            "experience_years",
            "deadline",
            "is_active",
            "source",
            "apply_url",
            "applications_count",
            "created_at",
        )
        read_only_fields = ("posted_by", "source")


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    applicant_name = serializers.CharField(source="applicant.full_name", read_only=True)

    class Meta:
        model = JobApplication
        fields = (
            "id",
            "uuid",
            "job",
            "job_title",
            "applicant",
            "applicant_name",
            "cover_letter",
            "cv",
            "status",
            "created_at",
        )
        read_only_fields = ("applicant", "status")
