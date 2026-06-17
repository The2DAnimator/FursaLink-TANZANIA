from django.contrib import admin

from apps.marketprices.models import Market, MarketPrice


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    list_filter = ("region",)
    search_fields = ("name",)


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ("product", "category", "market", "price", "unit", "date")
    list_filter = ("category", "region", "market")
    search_fields = ("product",)
    date_hierarchy = "date"
