from django.contrib import admin

from apps.opportunities.models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "posted_by", "industry", "region", "status", "deadline")
    list_filter = ("type", "status", "industry", "region")
    search_fields = ("title", "description", "industry")
    list_editable = ("status",)
