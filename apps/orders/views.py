from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.utils import record_attestation
from apps.cart import services as cart_services
from apps.core.models import SiteConfiguration
from apps.marketing.models import PromoCode

from .forms import CheckoutForm
from .models import Order
from .services import OutOfStock, place_order


def _get_promo(request):
    code = request.session.get("promo_code")
    return PromoCode.objects.filter(code=code, active=True).first() if code else None


def checkout(request):
    cfg = SiteConfiguration.get_solo()
    if cfg.catalog_mode:
        messages.info(request, "Online ordering is currently unavailable.")
        return redirect("core:home")

    cart = cart_services.get_cart(request, create=False)
    if not cart or not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    promo = _get_promo(request)
    totals = cart_services.cart_totals(request, cart=cart, promo=promo)
    needs_shipping = totals["has_ship"]
    needs_age = cart.has_ammo

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "phone": request.user.phone,
        }

    form = CheckoutForm(
        request.POST or None,
        initial=initial,
        needs_shipping=needs_shipping,
        needs_age=needs_age,
    )

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        contact = {
            "first_name": cd["first_name"],
            "last_name": cd["last_name"],
            "email": cd["email"],
            "phone": cd["phone"],
            "user": request.user if request.user.is_authenticated else None,
        }
        shipping = {
            "name": f"{cd['first_name']} {cd['last_name']}",
            "street": cd["ship_street"],
            "city": cd["ship_city"],
            "state": cd["ship_state"],
            "zip": cd["ship_zip"],
        } if needs_shipping else {}

        try:
            order = place_order(
                cart=cart, totals=totals, contact=contact,
                shipping=shipping, promo=promo,
            )
        except OutOfStock as e:
            messages.error(request, f"Sorry — not enough stock for {e.item.product.title}.")
            return redirect("cart:detail")

        if needs_age:
            record_attestation(
                request, email=cd["email"], context="checkout",
                order=order, user=request.user,
            )

        request.session.pop("promo_code", None)
        request.session["order_access"] = order.number
        return redirect("orders:confirmation", number=order.number)

    return render(
        request,
        "orders/checkout.html",
        {
            "cart": cart,
            "totals": totals,
            "form": form,
            "needs_shipping": needs_shipping,
            "needs_age": needs_age,
        },
    )


def confirmation(request, number):
    order = get_object_or_404(Order, number=number)
    # Guard: owner or the session that just placed it
    allowed = (
        request.user.is_authenticated and order.user_id == request.user.id
    ) or request.session.get("order_access") == number
    if not allowed:
        messages.error(request, "You don't have access to that order.")
        return redirect("core:home")
    return render(request, "orders/confirmation.html", {"order": order})
