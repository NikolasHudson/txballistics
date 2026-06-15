from django.conf import settings
from django.db import models


class Review(models.Model):
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    display_name = models.CharField(max_length=80)
    rating = models.PositiveSmallIntegerField(default=5)
    body = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.display_name} — {self.rating}★ on {self.product}"

    @property
    def stars(self):
        return "★★★★★"[: self.rating] + "☆☆☆☆☆"[: 5 - self.rating]
