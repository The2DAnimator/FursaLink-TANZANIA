from django.contrib import admin

from apps.core.models import AuditLog, Category, District, Region, SiteSetting


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    list_filter = ("region",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "parent")
    list_filter = ("kind",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "status_code", "ip_address", "created_at")
    list_filter = ("method", "status_code")
    search_fields = ("action", "path", "ip_address")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description")
    search_fields = ("key",)
