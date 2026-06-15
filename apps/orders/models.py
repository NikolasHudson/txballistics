from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


class Order(models.Model):
    STATUS_RESERVED = "reserved"
    STATUS_READY = "ready"
    STATUS_SHIPPED = "shipped"
    STATUS_PICKED_UP = "picked_up"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_RESERVED, "Reserved"),
        (STATUS_READY, "Ready for Pickup"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_PICKED_UP, "Picked Up"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PAYMENT_PICKUP = "pay_at_pickup"
    PAYMENT_ONLINE = "pay_now"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_PICKUP, "Pay at pickup"),
        (PAYMENT_ONLINE, "Pay now (card)"),
    ]

    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PAID = "paid"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PAID, "Paid"),
    ]

    number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders",
    )

    # Contact snapshot (email always required)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)

    # Fulfillment
    has_pickup_items = models.BooleanField(default=False)
    has_ship_items = models.BooleanField(default=False)
    ship_name = models.CharField(max_length=160, blank=True)
    ship_street = models.CharField(max_length=200, blank=True)
    ship_city = models.CharField(max_length=80, blank=True)
    ship_state = models.CharField(max_length=2, blank=True)
    ship_zip = models.CharField(max_length=10, blank=True)

    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_RESERVED
    )
    payment_method = models.CharField(
        max_length=16, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_PICKUP
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_UNPAID
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    promo_code = models.ForeignKey(
        "marketing.PromoCode", on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        for _ in range(20):
            num = "TX-" + get_random_string(5, "0123456789")
            if not Order.objects.filter(number=num).exists():
                return num
        return "TX-" + get_random_string(8, "0123456789")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def pickup_items(self):
        return [i for i in self.items.all() if i.fulfillment == "pickup"]

    @property
    def ship_items(self):
        return [i for i in self.items.all() if i.fulfillment == "ship"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.SET_NULL, null=True, blank=True
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.SET_NULL, null=True, blank=True
    )
    # Snapshot fields (survive product edits/deletes)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=64)
    variant_name = models.CharField(max_length=80, blank=True)
    caliber_label = models.CharField(max_length=12, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    fulfillment = models.CharField(max_length=10, default="pickup")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} × {self.title}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
