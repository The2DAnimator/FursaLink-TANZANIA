from django.contrib import admin

from apps.jobs.models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "type", "region", "deadline", "is_active")
    list_filter = ("type", "is_active", "source", "region", "category")
    search_fields = ("title", "company", "description")
    date_hierarchy = "deadline"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("job__title", "applicant__email")
    list_editable = ("status",)
