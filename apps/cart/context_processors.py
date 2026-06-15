from apps.cart.services import get_cart


def cart_summary(request):
    cart = get_cart(request, create=False)
    count = cart.count if cart else 0
    return {"cart_count": count}
