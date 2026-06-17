from django.contrib import admin

from apps.leads.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("business", "type", "status", "score", "industry", "created_at")
    list_filter = ("type", "status")
    search_fields = ("business__name", "contact_name", "industry")
    list_editable = ("status",)
