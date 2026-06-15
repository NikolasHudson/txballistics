from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import AgeAttestation, SavedItem, User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "is_staff", "member_since"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "phone", "customer_tier", "member_since")}),
        ("Notifications", {"fields": (
            "notify_pickup_email", "notify_restock_email", "notify_weekly_deals",
        )}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )


@admin.register(SavedItem)
class SavedItemAdmin(ModelAdmin):
    list_display = ["user", "product", "created_at"]
    search_fields = ["user__email", "product__title"]


@admin.register(AgeAttestation)
class AgeAttestationAdmin(ModelAdmin):
    list_display = ["email", "context", "order", "attested_at", "ip_address"]
    list_filter = ["context", "attested_at"]
    search_fields = ["email"]
    readonly_fields = [
        "user", "email", "context", "order", "statement_version",
        "ip_address", "user_agent", "attested_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
