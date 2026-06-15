from decimal import Decimal

from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name="cart",
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.pk}"

    @property
    def items_list(self):
        return list(self.items.select_related("product", "variant"))

    @property
    def count(self):
        return sum(i.quantity for i in self.items.all())

    @property
    def subtotal(self):
        return sum((i.line_total for i in self.items_list), Decimal("0"))

    @property
    def has_ammo(self):
        return any(i.product.product_type == "ammo" for i in self.items_list)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("cart", "product", "variant")]
        ordering = ["added_at"]

    def __str__(self):
        return f"{self.quantity} × {self.product}"

    @property
    def unit_price(self):
        return self.variant.price if self.variant else self.product.current_price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def available_stock(self):
        return self.variant.stock if self.variant else self.product.total_stock

    @property
    def fulfillment(self):
        return self.product.resolved_fulfillment
