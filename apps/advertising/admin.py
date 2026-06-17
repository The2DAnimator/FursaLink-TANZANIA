from django.contrib import admin

from apps.advertising.models import AdPlan, Advertisement


@admin.register(AdPlan)
class AdPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "placement", "price", "duration_days", "is_active")
    list_filter = ("placement", "is_active")


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("title", "advertiser", "plan", "status", "ends_at", "impressions", "clicks")
    list_filter = ("status", "plan")
    search_fields = ("title", "advertiser__email")
    list_editable = ("status",)
