"""Cart service layer: session/user cart, totals, mutations."""
from decimal import Decimal

from apps.cart.models import Cart, CartItem
from apps.core.models import SiteConfiguration

CART_SESSION_KEY = "cart_id"


def _ensure_session(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def get_cart(request, create=True):
    """Return the active cart for this request (user or session), or None."""
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        cart = Cart.objects.filter(user=user).first()
        if cart is None and create:
            cart = Cart.objects.create(user=user)
        return cart

    cart_id = request.session.get(CART_SESSION_KEY)
    cart = Cart.objects.filter(pk=cart_id, user__isnull=True).first() if cart_id else None
    if cart is None and create:
        cart = Cart.objects.create(session_key=_ensure_session(request))
        request.session[CART_SESSION_KEY] = cart.pk
    return cart


def merge_session_into_user(request, user):
    """On login, fold the guest cart into the user's cart."""
    cart_id = request.session.get(CART_SESSION_KEY)
    if not cart_id:
        return
    guest = Cart.objects.filter(pk=cart_id, user__isnull=True).first()
    if not guest:
        return
    user_cart, _ = Cart.objects.get_or_create(user=user)
    for item in guest.items.all():
        existing = user_cart.items.filter(
            product=item.product, variant=item.variant
        ).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()
    guest.delete()
    request.session.pop(CART_SESSION_KEY, None)


def add_item(request, product, variant=None, quantity=1):
    cart = get_cart(request, create=True)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variant=variant,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save()
    return cart, item


def update_item(request, item_id, quantity):
    cart = get_cart(request, create=False)
    if not cart:
        return None
    item = cart.items.filter(pk=item_id).first()
    if item:
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
    return cart


def remove_item(request, item_id):
    cart = get_cart(request, create=False)
    if cart:
        cart.items.filter(pk=item_id).delete()
    return cart


def cart_totals(request, cart=None, promo=None):
    """Compute totals. Shipping only applies when shipping is enabled + ship items present."""
    cfg = SiteConfiguration.get_solo()
    if cart is None:
        cart = get_cart(request, create=False)
    if cart is None:
        return _empty_totals()

    items = cart.items_list
    subtotal = sum((i.line_total for i in items), Decimal("0"))

    discount = Decimal("0")
    if promo is not None:
        discount = promo.discount_for(subtotal)

    taxable = max(subtotal - discount, Decimal("0"))
    tax = (taxable * cfg.tax_rate).quantize(Decimal("0.01"))

    has_ship = any(i.fulfillment == "ship" for i in items)
    ship_subtotal = sum(
        (i.line_total for i in items if i.fulfillment == "ship"), Decimal("0")
    )
    shipping = Decimal("0")
    if has_ship:
        if ship_subtotal >= cfg.free_shipping_threshold:
            shipping = Decimal("0")
        else:
            shipping = cfg.shipping_flat_rate

    total = taxable + tax + shipping
    return {
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "discount": discount.quantize(Decimal("0.01")),
        "tax": tax,
        "shipping": shipping,
        "total": total.quantize(Decimal("0.01")),
        "has_ship": has_ship,
        "has_pickup": any(i.fulfillment == "pickup" for i in items),
        "count": cart.count,
    }


def _empty_totals():
    z = Decimal("0.00")
    return {
        "subtotal": z, "discount": z, "tax": z, "shipping": z, "total": z,
        "has_ship": False, "has_pickup": False, "count": 0,
    }
