from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "first_name", "last_name", "is_staff",
                    "is_active", "email_verified"]
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal", {
            "fields": ("first_name", "last_name", "profile_image",
                       "email_verified"),
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser",
                       "groups", "user_permissions"),
        }),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name",
                       "password1", "password2"),
        }),
    )
