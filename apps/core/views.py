from django.shortcuts import render

from apps.catalog.models import Category, Product
from apps.marketing.models import Testimonial


def home(request):
    hero = (
        Product.objects.filter(is_hero_deal=True, is_active=True)
        .select_related("category")
        .first()
    )
    specials = (
        Product.objects.filter(is_special=True, is_active=True)
        .select_related("category")[:5]
    )
    categories = Category.objects.filter(parent__isnull=True, is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)
    testimonials_data = [{"text": t.quote, "who": t.author} for t in testimonials]
    return render(
        request,
        "core/home.html",
        {
            "hero": hero,
            "specials": specials,
            "categories": categories,
            "testimonials": testimonials,
            "testimonials_data": testimonials_data,
        },
    )


def about(request):
    return render(request, "core/about.html")
