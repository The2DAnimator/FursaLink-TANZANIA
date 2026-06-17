from django.contrib import admin

from apps.subscriptions.models import Payment, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price", "max_listings", "has_analytics", "featured_placement")
    list_filter = ("tier",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "started_at", "expires_at", "auto_renew")
    list_filter = ("status", "plan")
    search_fields = ("user__email",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "amount", "provider", "purpose", "status", "created_at")
    list_filter = ("status", "provider", "purpose")
    search_fields = ("reference", "user__email", "provider_ref")
    readonly_fields = ("reference", "provider_ref", "metadata")
