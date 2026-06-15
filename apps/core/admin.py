from django.contrib import admin
from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin

from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin, ModelAdmin):
    fieldsets = (
        ("Branding", {"fields": ("primary_color", "guarantee_copy")}),
        ("Contact", {"fields": ("store_phone", "store_email")}),
        ("Pickup", {"fields": ("pickup_address", "pickup_instructions")}),
        ("Feature flags", {
            "fields": (
                "catalog_mode", "show_stock", "fishing_shipping_enabled",
                "reviews_enabled",
            ),
        }),
        ("Commerce", {
            "fields": (
                "tax_rate", "shipping_flat_rate", "free_shipping_threshold",
                "active_payment_provider",
            ),
        }),
    )
