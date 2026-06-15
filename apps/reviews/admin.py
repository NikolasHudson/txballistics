from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

from .models import Review


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ["display_name", "product", "rating", "is_approved", "is_verified", "created_at"]
    list_filter = ["is_approved", "is_verified", "rating"]
    search_fields = ["display_name", "product__title", "body"]
    actions_list = ["approve"]

    @action(description="Approve selected", icon="check", variant=ActionVariant.SUCCESS)
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
