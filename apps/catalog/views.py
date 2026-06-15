from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product, ProductType

SORTS = {
    "cpr": ("Cost Per Round (low → high)", ["price"]),
    "price_asc": ("Price (low → high)", ["price"]),
    "price_desc": ("Price (high → low)", ["-price"]),
    "manufacturer": ("Manufacturer", ["manufacturer__name", "title"]),
    "grain": ("Bullet Weight", ["grain"]),
    "top": ("Top Rated", ["-id"]),
}


def category(request, slug):
    cat = get_object_or_404(Category, slug=slug, is_active=True)

    # Products in this category or any descendant
    descendant_ids = [cat.id] + list(cat.children.values_list("id", flat=True))
    qs = (
        Product.objects.filter(category_id__in=descendant_ids, is_active=True)
        .select_related("manufacturer", "category")
    )

    # Filters
    bullet = request.GET.getlist("bullet")
    casing = request.GET.getlist("casing")
    if bullet:
        qs = qs.filter(bullet_type__in=bullet)
    if casing:
        qs = qs.filter(casing__in=casing)

    # Sort
    sort = request.GET.get("sort", "price_asc")
    order = SORTS.get(sort, SORTS["price_asc"])[1]
    qs = qs.order_by(*order)

    total = qs.count()

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page"))

    # Sibling subcategories for the sidebar
    if cat.is_top_level:
        siblings = cat.children.filter(is_active=True)
        parent_title = cat.name
    else:
        siblings = cat.parent.children.filter(is_active=True)
        parent_title = cat.parent.name

    other_top = Category.objects.filter(parent__isnull=True, is_active=True).exclude(
        pk=cat.id if cat.is_top_level else cat.parent_id
    )

    return render(
        request,
        "catalog/category.html",
        {
            "category": cat,
            "products": page,
            "total": total,
            "siblings": siblings,
            "parent_title": parent_title,
            "other_top": other_top,
            "sorts": SORTS,
            "current_sort": sort,
            "is_tackle": cat.product_type == ProductType.TACKLE,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "manufacturer").prefetch_related(
            "variants", "specs", "images", "reviews"
        ),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)[:4]
    )
    reviews = product.reviews.filter(is_approved=True)
    template = (
        "catalog/product_tackle.html"
        if product.product_type == ProductType.TACKLE
        else "catalog/product_ammo.html"
    )
    return render(
        request,
        template,
        {
            "product": product,
            "related": related,
            "reviews": reviews,
            "variants": product.variants.filter(is_active=True),
        },
    )


def search(request):
    q = request.GET.get("q", "").strip()
    results = Product.objects.none()
    if q:
        results = (
            Product.objects.filter(is_active=True)
            .filter(
                Q(title__icontains=q)
                | Q(sku__icontains=q)
                | Q(caliber_label__icontains=q)
                | Q(manufacturer__name__icontains=q)
                | Q(category__name__icontains=q)
            )
            .select_related("category", "manufacturer")
            .distinct()
        )
    paginator = Paginator(results, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "catalog/search.html",
        {"q": q, "products": page, "total": results.count() if q else 0},
    )
