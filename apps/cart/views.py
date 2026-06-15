from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product, ProductVariant
from apps.core.models import SiteConfiguration
from apps.marketing.models import PromoCode

from . import services


def _catalog_mode_block(request):
    if SiteConfiguration.get_solo().catalog_mode:
        messages.info(request, "Online ordering is currently unavailable. Please call to order.")
        return True
    return False


def _get_promo(request):
    code = request.session.get("promo_code")
    if not code:
        return None
    return PromoCode.objects.filter(code=code, active=True).first()


def detail(request):
    cart = services.get_cart(request, create=False)
    promo = _get_promo(request)
    totals = services.cart_totals(request, cart=cart, promo=promo)
    return render(
        request,
        "cart/detail.html",
        {"cart": cart, "totals": totals, "promo": promo},
    )


@require_POST
def add(request):
    if _catalog_mode_block(request):
        return redirect("cart:detail")
    product = get_object_or_404(Product, pk=request.POST.get("product_id"), is_active=True)
    variant = None
    variant_id = request.POST.get("variant_id")
    if variant_id:
        variant = get_object_or_404(ProductVariant, pk=variant_id, product=product)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1
    services.add_item(request, product, variant=variant, quantity=quantity)
    cart = services.get_cart(request, create=False)
    if request.htmx:
        resp = HttpResponse(str(cart.count if cart else 0))
        resp["HX-Trigger"] = "cart-updated"
        return resp
    messages.success(request, f"Added {product.title} to your cart.")
    return redirect(request.META.get("HTTP_REFERER", "cart:detail"))


@require_POST
def update(request):
    item_id = request.POST.get("item_id")
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    services.update_item(request, item_id, quantity)
    return _cart_fragment_or_redirect(request)


@require_POST
def remove(request):
    services.remove_item(request, request.POST.get("item_id"))
    return _cart_fragment_or_redirect(request)


@require_POST
def apply_promo(request):
    code = request.POST.get("code", "").strip()
    cart = services.get_cart(request, create=False)
    subtotal = cart.subtotal if cart else 0
    promo = PromoCode.objects.filter(code__iexact=code).first()
    if not promo:
        messages.error(request, "That promo code wasn't found.")
        request.session.pop("promo_code", None)
    else:
        ok, msg = promo.is_valid(subtotal)
        if ok:
            request.session["promo_code"] = promo.code
            messages.success(request, f"Promo code {promo.code} applied.")
        else:
            messages.error(request, msg)
            request.session.pop("promo_code", None)
    return redirect("cart:detail")


def _cart_fragment_or_redirect(request):
    cart = services.get_cart(request, create=False)
    promo = _get_promo(request)
    totals = services.cart_totals(request, cart=cart, promo=promo)
    if request.htmx:
        return render(
            request,
            "cart/_cart_body.html",
            {"cart": cart, "totals": totals, "promo": promo},
        )
    return redirect("cart:detail")
