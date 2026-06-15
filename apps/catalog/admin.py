from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Category, Manufacturer, Product, ProductImage, ProductSpec, ProductVariant


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "parent", "product_type", "order", "is_active"]
    list_filter = ["product_type", "is_active", "parent"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Manufacturer)
class ManufacturerAdmin(ModelAdmin):
    list_display = ["name", "short_name", "is_house_brand"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 0


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0


class ProductSpecInline(TabularInline):
    model = ProductSpec
    extra = 0


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = [
        "title", "category", "product_type", "price_display", "stock_badge",
        "is_active", "is_featured", "is_hero_deal",
    ]
    list_filter = [
        "product_type", "is_active", "is_featured", "is_special", "is_hero_deal",
        "category", "manufacturer", "bullet_type", "casing",
    ]
    search_fields = ["title", "sku", "caliber_label"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["is_active", "is_featured"]
    inlines = [ProductVariantInline, ProductImageInline, ProductSpecInline]
    list_select_related = ["category", "manufacturer"]
    fieldsets = (
        (None, {"fields": (
            "title", "slug", "sku", "category", "manufacturer", "product_type",
            "fulfillment", "caliber_label", "image", "description",
        )}),
        ("Pricing & stock", {"fields": (
            "price", "sale_price", "stock",
            "is_active", "is_featured", "is_special", "is_hero_deal",
        )}),
        ("Ammo attributes", {"fields": (
            "grain", "bullet_type", "casing", "rounds_per_unit", "use_type",
            "primer", "muzzle_velocity", "muzzle_energy", "is_magnetic",
        ), "classes": ["collapse"]}),
    )

    @display(description="Price")
    def price_display(self, obj):
        if obj.is_on_sale:
            return f"${obj.sale_price} (was ${obj.price})"
        return f"${obj.price}"

    @display(description="Stock", label={"in": "success", "low": "warning", "out": "danger"})
    def stock_badge(self, obj):
        return obj.stock_status
