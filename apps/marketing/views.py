from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .models import NewsletterSubscriber, RestockAlert


@require_POST
def subscribe(request):
    email = request.POST.get("email", "").strip().lower()
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
        if request.htmx:
            return HttpResponse("<p class='newsletter-thanks'>Thanks — you're on the list!</p>")
        messages.success(request, "Thanks — you're on the list!")
    return redirect(request.META.get("HTTP_REFERER", "core:home"))


@require_POST
def restock_notify(request):
    product = get_object_or_404(Product, pk=request.POST.get("product_id"))
    email = request.POST.get("email", "").strip().lower()
    if request.user.is_authenticated and not email:
        email = request.user.email
    if email:
        RestockAlert.objects.get_or_create(
            email=email, product=product,
            user=request.user if request.user.is_authenticated else None,
        )
        if request.htmx:
            return HttpResponse("✓ We'll email you when it's back.")
        messages.success(request, "We'll email you when it's back in stock.")
    return redirect(request.META.get("HTTP_REFERER", "core:home"))
