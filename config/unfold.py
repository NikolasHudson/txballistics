"""Unfold admin configuration + runtime callbacks (DB-driven brand color)."""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def _hex_to_rgb(value: str) -> str:
    """Convert '#2f5d3a' -> '47 93 58' (the space-separated rgb Unfold accepts)."""
    value = (value or "").lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    try:
        r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
        return f"{r} {g} {b}"
    except (ValueError, IndexError):
        return "47 93 58"  # fallback forest green


def primary_palette(request):
    """Drive the admin's primary color from SiteConfiguration.primary_color."""
    try:
        from apps.core.models import SiteConfiguration

        base = SiteConfiguration.get_solo().primary_color
    except Exception:
        base = "#2f5d3a"
    rgb = _hex_to_rgb(base)
    # v1: flat ramp (same color across weights). Good enough; swap for a real
    # 50-950 scale later if the client wants tonal depth.
    return {str(w): rgb for w in (50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950)}


def dashboard_callback(request, context):
    """Inject KPI cards onto the Unfold dashboard."""
    try:
        from apps.catalog.models import Product
        from apps.orders.models import Order

        context["kpi"] = [
            {
                "title": _("Orders awaiting pickup"),
                "metric": Order.objects.filter(status__in=["reserved", "ready"]).count(),
            },
            {
                "title": _("Low stock (≤12)"),
                "metric": Product.objects.filter(is_active=True, stock__lte=12).count(),
            },
            {
                "title": _("Active products"),
                "metric": Product.objects.filter(is_active=True).count(),
            },
            {
                "title": _("Total orders"),
                "metric": Order.objects.count(),
            },
        ]
    except Exception:
        context["kpi"] = []
    return context


UNFOLD = {
    "SITE_TITLE": "TX Ballistics Admin",
    "SITE_HEADER": "TX Ballistics",
    "SITE_SUBHEADER": _("Back office"),
    "SITE_SYMBOL": "store",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "config.unfold.dashboard_callback",
    "COLORS": {
        "primary": "config.unfold.primary_palette",
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": _("Catalog"),
                "separator": True,
                "items": [
                    {
                        "title": _("Products"),
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:catalog_product_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:catalog_category_changelist"),
                    },
                    {
                        "title": _("Manufacturers"),
                        "icon": "factory",
                        "link": reverse_lazy("admin:catalog_manufacturer_changelist"),
                    },
                ],
            },
            {
                "title": _("Sales"),
                "separator": True,
                "items": [
                    {
                        "title": _("Orders"),
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                    {
                        "title": _("Payments"),
                        "icon": "payments",
                        "link": reverse_lazy("admin:payments_payment_changelist"),
                    },
                    {
                        "title": _("Promo Codes"),
                        "icon": "sell",
                        "link": reverse_lazy("admin:marketing_promocode_changelist"),
                    },
                ],
            },
            {
                "title": _("Customers"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": _("Reviews"),
                        "icon": "star",
                        "link": reverse_lazy("admin:reviews_review_changelist"),
                    },
                    {
                        "title": _("Age Attestations"),
                        "icon": "verified_user",
                        "link": reverse_lazy("admin:accounts_ageattestation_changelist"),
                    },
                ],
            },
            {
                "title": _("Marketing"),
                "separator": True,
                "items": [
                    {
                        "title": _("Testimonials"),
                        "icon": "format_quote",
                        "link": reverse_lazy("admin:marketing_testimonial_changelist"),
                    },
                    {
                        "title": _("Newsletter"),
                        "icon": "mail",
                        "link": reverse_lazy("admin:marketing_newslettersubscriber_changelist"),
                    },
                    {
                        "title": _("Restock Alerts"),
                        "icon": "notifications",
                        "link": reverse_lazy("admin:marketing_restockalert_changelist"),
                    },
                ],
            },
            {
                "title": _("Settings"),
                "separator": True,
                "items": [
                    {
                        "title": _("Site Configuration"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_siteconfiguration_changelist"),
                    },
                ],
            },
        ],
    },
}
