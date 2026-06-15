from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from unfold.enums import ActionVariant

from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        "product", "variant", "title", "sku", "variant_name",
        "unit_price", "quantity", "fulfillment",
    ]
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "full_name", "status_badge", "total", "created_at"]
    list_filter = ["status", "payment_status", "has_ship_items", "created_at"]
    search_fields = ["number", "email", "first_name", "last_name"]
    inlines = [OrderItemInline]
    readonly_fields = ["number", "created_at", "ready_at", "shipped_at", "picked_up_at"]
    actions_list = ["mark_ready", "mark_picked_up"]

    @display(description="Status", label={
        "reserved": "info", "ready": "warning", "shipped": "info",
        "picked_up": "success", "completed": "success", "cancelled": "danger",
    })
    def status_badge(self, obj):
        return obj.status

    @action(description="Mark Ready for Pickup", icon="check", variant=ActionVariant.WARNING)
    def mark_ready(self, request, queryset):
        queryset.update(status=Order.STATUS_READY, ready_at=timezone.now())

    @action(description="Mark Picked Up", icon="done_all", variant=ActionVariant.SUCCESS)
    def mark_picked_up(self, request, queryset):
        queryset.update(status=Order.STATUS_PICKED_UP, picked_up_at=timezone.now())
