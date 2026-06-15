from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Testimonial(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=120, help_text="e.g. 'Dale R., Round Rock'")
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.author}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class RestockAlert(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.CASCADE, null=True, blank=True
    )
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} → {self.product}"


class PromoCode(models.Model):
    KIND_PERCENT = "percent"
    KIND_FIXED = "fixed"
    KIND_CHOICES = [
        (KIND_PERCENT, "Percent off"),
        (KIND_FIXED, "Fixed amount off"),
    ]

    code = models.CharField(max_length=40, unique=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_PERCENT)
    value = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Percent (e.g. 10 = 10%) or fixed dollar amount.",
    )
    active = models.BooleanField(default=True)
    starts = models.DateTimeField(null=True, blank=True)
    ends = models.DateTimeField(null=True, blank=True)
    min_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    def is_valid(self, subtotal):
        now = timezone.now()
        if not self.active:
            return False, "This code is not active."
        if self.starts and now < self.starts:
            return False, "This code isn't available yet."
        if self.ends and now > self.ends:
            return False, "This code has expired."
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False, "This code has reached its usage limit."
        if subtotal < self.min_subtotal:
            return False, f"Requires a subtotal of at least ${self.min_subtotal}."
        return True, ""

    def discount_for(self, subtotal):
        ok, _ = self.is_valid(subtotal)
        if not ok:
            return Decimal("0")
        if self.kind == self.KIND_PERCENT:
            disc = (subtotal * self.value / Decimal("100"))
        else:
            disc = self.value
        disc = min(disc, subtotal)
        return disc.quantize(Decimal("0.01"))
