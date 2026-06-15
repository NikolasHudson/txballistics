from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ["order", "provider", "amount", "status", "created_at"]
    list_filter = ["provider", "status"]
    search_fields = ["order__number", "external_ref"]
