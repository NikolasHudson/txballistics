from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from apps.catalog.models import Product
from apps.core.models import SiteConfiguration

from .models import Review


def create(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if not SiteConfiguration.get_solo().reviews_enabled:
        messages.error(request, "Reviews are currently disabled.")
        return redirect(product.get_absolute_url())
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5) or 5)
        body = request.POST.get("body", "").strip()
        if request.user.is_authenticated:
            display_name = request.user.full_name
        else:
            display_name = request.POST.get("display_name", "Anonymous").strip() or "Anonymous"
        if body:
            Review.objects.create(
                product=product,
                author=request.user if request.user.is_authenticated else None,
                display_name=display_name,
                rating=max(1, min(5, rating)),
                body=body,
            )
            messages.success(request, "Thanks! Your review will appear once approved.")
        else:
            messages.error(request, "Please write a few words for your review.")
    return redirect(product.get_absolute_url() + "#reviews")
