from django.db import models
from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    """Backend-editable control panel + feature flags."""

    # Branding
    primary_color = models.CharField(
        max_length=7, default="#2f5d3a",
        help_text="Storefront + admin primary color (hex, e.g. #2f5d3a).",
    )
    guarantee_copy = models.CharField(
        max_length=120, default="$100 Guarantee",
        help_text="Short trust/guarantee text shown in the header.",
    )

    # Contact (shown in header/footer/confirmation)
    store_phone = models.CharField(max_length=32, default="(512) 555-0142")
    store_email = models.EmailField(default="howdy@txballistics.com")

    # Pickup (revealed after ordering)
    pickup_address = models.TextField(
        default="1487 Ranch Road\nDripping Springs, TX 78620",
        help_text="Revealed to the customer after they place an order.",
    )
    pickup_instructions = models.TextField(
        blank=True,
        default="Bring a valid photo ID and the card used to order. "
        "We'll email you when your order is bagged and ready.",
    )

    # Feature flags
    catalog_mode = models.BooleanField(
        default=False,
        help_text="Browse-only: hides cart/checkout and disables online ordering.",
    )
    show_stock = models.BooleanField(
        default=False,
        help_text="Show stock counts/badges across the storefront.",
    )
    fishing_shipping_enabled = models.BooleanField(
        default=False,
        help_text="When on, fishing/tackle ships instead of pickup.",
    )
    reviews_enabled = models.BooleanField(
        default=True,
        help_text="Show customer reviews and allow shoppers to submit them.",
    )

    # Commerce
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default="0.0825")
    shipping_flat_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default="7.99"
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=8, decimal_places=2, default="35.00"
    )

    active_payment_provider = models.CharField(
        max_length=32, default="manual",
        help_text="Key of the active payment provider (e.g. 'manual').",
    )

    class Meta:
        verbose_name = "Site Configuration"

    def __str__(self):
        return "Site Configuration"
