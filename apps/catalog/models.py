from decimal import Decimal

from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.text import slugify


class ProductType(models.TextChoices):
    AMMO = "ammo", "Ammo"
    TACKLE = "tackle", "Fishing / Tackle"


class Fulfillment(models.TextChoices):
    PICKUP = "pickup", "Pickup"
    SHIP = "ship", "Ship"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    product_type = models.CharField(
        max_length=10, choices=ProductType.choices, default=ProductType.AMMO
    )
    blurb = models.TextField(blank=True, help_text="Intro text under the listing title.")
    quick_facts = models.TextField(
        blank=True, help_text="One bullet per line (SEO/info section)."
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category", args=[self.slug])

    @property
    def is_top_level(self):
        return self.parent_id is None

    @property
    def quick_facts_list(self):
        return [line.strip() for line in self.quick_facts.splitlines() if line.strip()]


class Manufacturer(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    short_name = models.CharField(max_length=40, blank=True)
    is_house_brand = models.BooleanField(default=False)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    sku = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products",
    )
    product_type = models.CharField(
        max_length=10, choices=ProductType.choices, default=ProductType.AMMO
    )
    fulfillment = models.CharField(
        max_length=10, choices=Fulfillment.choices, blank=True,
        help_text="Leave blank to derive from type (ammo=pickup, tackle=pickup until "
        "shipping is enabled).",
    )

    # Commerce
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_special = models.BooleanField(default=False)
    is_hero_deal = models.BooleanField(
        default=False, help_text="Homepage 'Deal of the Day'. Only one at a time."
    )

    # Display
    caliber_label = models.CharField(
        max_length=12, blank=True, help_text="Text/emoji shown on the product tile."
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    # Ammo attributes (nullable; drive table columns + filters)
    grain = models.PositiveIntegerField(null=True, blank=True)
    bullet_type = models.CharField(max_length=64, blank=True)
    casing = models.CharField(max_length=32, blank=True)
    rounds_per_unit = models.PositiveIntegerField(null=True, blank=True)
    use_type = models.CharField(max_length=64, blank=True)
    primer = models.CharField(max_length=32, blank=True)
    muzzle_velocity = models.PositiveIntegerField(null=True, blank=True)
    muzzle_energy = models.PositiveIntegerField(null=True, blank=True)
    is_magnetic = models.BooleanField(default=False)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["product_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:280]
        # Enforce single hero deal
        if self.is_hero_deal:
            Product.objects.exclude(pk=self.pk).filter(is_hero_deal=True).update(
                is_hero_deal=False
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    # ---- derived ----
    @property
    def current_price(self):
        return self.sale_price if self.sale_price is not None else self.price

    @property
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def savings(self):
        return (self.price - self.sale_price) if self.is_on_sale else Decimal("0")

    @property
    def cost_per_round(self):
        if self.rounds_per_unit:
            return (self.current_price / self.rounds_per_unit).quantize(Decimal("0.01"))
        return None

    @property
    def cost_per_round_cents(self):
        cpr = self.cost_per_round
        return f"{int(round(cpr * 100))}¢" if cpr is not None else ""

    @property
    def total_stock(self):
        if self.pk and self.variants.exists():
            return sum(v.stock for v in self.variants.all())
        return self.stock

    @property
    def in_stock(self):
        return self.total_stock > 0

    @property
    def stock_status(self):
        s = self.total_stock
        if s == 0:
            return "out"
        if s <= 12:
            return "low"
        return "in"

    @property
    def resolved_fulfillment(self):
        """Pickup unless this is tackle AND shipping is enabled site-wide."""
        from apps.core.models import SiteConfiguration

        if self.fulfillment:
            base = self.fulfillment
        else:
            base = (
                Fulfillment.SHIP
                if self.product_type == ProductType.TACKLE
                else Fulfillment.PICKUP
            )
        if base == Fulfillment.SHIP and not SiteConfiguration.get_solo().fishing_shipping_enabled:
            return Fulfillment.PICKUP
        return base

    @property
    def rating_data(self):
        agg = self.reviews.filter(is_approved=True).aggregate(
            avg=Avg("rating"), n=Count("id")
        )
        return {"avg": agg["avg"] or 0, "count": agg["n"] or 0}

    @property
    def avg_rating(self):
        return self.rating_data["avg"]

    @property
    def review_count(self):
        return self.rating_data["count"]

    @property
    def has_variants(self):
        return self.variants.exists()


class ProductVariant(models.Model):
    """Per-color/pattern variant (fishing tackle) with its own SKU + stock."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=80)
    sku_suffix = models.CharField(max_length=32, blank=True)
    swatch_color_1 = models.CharField(max_length=7, blank=True, default="#cccccc")
    swatch_color_2 = models.CharField(max_length=7, blank=True, default="#888888")
    stock = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.product.title} — {self.name}"

    @property
    def sku(self):
        return f"{self.product.sku}-{self.sku_suffix}" if self.sku_suffix else self.product.sku

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.current_price


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.alt or f"Image #{self.pk}"


class ProductSpec(models.Model):
    """Free-form spec rows for the detail page (esp. tackle)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specs"
    )
    label = models.CharField(max_length=80)
    value = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.label}: {self.value}"
