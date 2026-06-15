from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import NewsletterSubscriber, PromoCode, RestockAlert, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ["author", "rating", "is_active", "order"]
    list_editable = ["is_active", "order"]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ["email", "is_active", "created_at"]
    search_fields = ["email"]


@admin.register(RestockAlert)
class RestockAlertAdmin(ModelAdmin):
    list_display = ["email", "product", "variant", "notified_at", "created_at"]
    list_filter = ["notified_at"]
    search_fields = ["email", "product__title"]


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = ["code", "kind", "value", "active", "used_count", "usage_limit"]
    list_filter = ["kind", "active"]
    search_fields = ["code"]
    fieldsets = (
        (None, {"fields": ("code", "kind", "value", "active")}),
        ("Limits", {"fields": ("min_subtotal", "usage_limit", "used_count", "starts", "ends")}),
    )
