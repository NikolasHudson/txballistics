from apps.catalog.models import Category
from apps.core.models import SiteConfiguration


def site_config(request):
    return {"site_config": SiteConfiguration.get_solo()}


def nav_categories(request):
    cats = (
        Category.objects.filter(parent__isnull=True, is_active=True)
        .order_by("order", "name")
    )
    return {"nav_categories": cats}
