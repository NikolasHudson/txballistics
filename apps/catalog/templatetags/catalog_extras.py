from django import template

register = template.Library()


@register.filter
def stars(value):
    """Render an integer/float 0-5 rating as filled/empty stars."""
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        n = 0
    n = max(0, min(5, n))
    return "★★★★★"[:n] + "☆☆☆☆☆"[: 5 - n]


@register.filter
def cents_per_round(product):
    return product.cost_per_round_cents
