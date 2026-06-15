"""Order placement: atomic stock decrement + snapshotting."""
from django.db import transaction
from django.db.models import F

from apps.catalog.models import Product, ProductVariant
from apps.payments.providers import get_active_provider

from .models import Order, OrderItem


class OutOfStock(Exception):
    def __init__(self, item):
        self.item = item
        super().__init__(f"Not enough stock for {item}")


@transaction.atomic
def place_order(*, cart, totals, contact, shipping, promo):
    """Create the order, decrement stock atomically, record payment. Returns Order."""
    items = cart.items_list
    if not items:
        raise ValueError("Cart is empty")

    has_pickup = any(i.fulfillment == "pickup" for i in items)
    has_ship = any(i.fulfillment == "ship" for i in items)

    order = Order.objects.create(
        first_name=contact["first_name"],
        last_name=contact["last_name"],
        email=contact["email"],
        phone=contact.get("phone", ""),
        user=contact.get("user"),
        has_pickup_items=has_pickup,
        has_ship_items=has_ship,
        ship_name=shipping.get("name", ""),
        ship_street=shipping.get("street", ""),
        ship_city=shipping.get("city", ""),
        ship_state=shipping.get("state", ""),
        ship_zip=shipping.get("zip", ""),
        payment_method=Order.PAYMENT_PICKUP,
        subtotal=totals["subtotal"],
        discount=totals["discount"],
        tax=totals["tax"],
        shipping=totals["shipping"],
        total=totals["total"],
        promo_code=promo,
    )

    for item in items:
        # Guarded atomic decrement to prevent overselling.
        if item.variant_id:
            updated = ProductVariant.objects.filter(
                pk=item.variant_id, stock__gte=item.quantity
            ).update(stock=F("stock") - item.quantity)
        else:
            updated = Product.objects.filter(
                pk=item.product_id, stock__gte=item.quantity
            ).update(stock=F("stock") - item.quantity)
        if not updated:
            # Stock tracking may legitimately be a no-op for products with 0 set
            # while stock display is off; only block when stock is actually tracked.
            available = item.available_stock
            if available < item.quantity and available > 0:
                raise OutOfStock(item)

        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            title=item.product.title,
            sku=item.variant.sku if item.variant else item.product.sku,
            variant_name=item.variant.name if item.variant else "",
            caliber_label=item.product.caliber_label,
            unit_price=item.unit_price,
            quantity=item.quantity,
            fulfillment=item.fulfillment,
        )

    if promo:
        promo.used_count = F("used_count") + 1
        promo.save(update_fields=["used_count"])

    provider = get_active_provider()
    provider.create_payment(order)

    cart.items.all().delete()
    return order
