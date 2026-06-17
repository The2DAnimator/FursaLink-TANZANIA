from django.contrib import admin

from apps.businesses.models import Business, Review


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "category", "region", "verification_status", "is_featured")
    list_filter = ("verification_status", "is_featured", "region", "category")
    search_fields = ("name", "description", "owner__email")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("verification_status", "is_featured")
    actions = ["mark_verified", "mark_featured"]

    @admin.action(description="Mark selected businesses as verified")
    def mark_verified(self, request, queryset):
        queryset.update(verification_status=Business.VerificationStatus.VERIFIED)

    @admin.action(description="Mark selected businesses as featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("business", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("business__name", "user__email")
