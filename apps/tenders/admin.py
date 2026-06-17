from django.contrib import admin

from apps.tenders.models import Tender


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ("tender_number", "organization", "sector", "closing_date", "is_active")
    list_filter = ("sector", "is_active", "source", "region")
    search_fields = ("tender_number", "organization", "title")
    date_hierarchy = "closing_date"
