from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import (
    EmailVerificationToken,
    JobSeekerProfile,
    PasswordResetToken,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("email", "first_name", "last_name", "role", "is_verified", "is_staff")
    list_filter = ("role", "is_verified", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "phone", "avatar", "region", "district")}),
        ("Role & verification", {"fields": ("role", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role"),
            },
        ),
    )


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "years_experience", "open_to_work")
    search_fields = ("user__email", "headline", "skills")


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "used_at")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "used_at")
