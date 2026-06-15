from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Email-login user manager (no username)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Custom user: email login, no government ID / DOB stored."""

    username = None
    email = models.EmailField("email address", unique=True)
    phone = models.CharField(max_length=32, blank=True)
    member_since = models.DateField(default=timezone.now)
    customer_tier = models.CharField(max_length=32, blank=True, default="")

    # Communication preferences (email only for v1)
    notify_pickup_email = models.BooleanField(default=True)
    notify_restock_email = models.BooleanField(default=True)
    notify_weekly_deals = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return (f"{self.first_name} {self.last_name}").strip() or self.email

    @property
    def initials(self):
        parts = [self.first_name, self.last_name]
        letters = "".join(p[0] for p in parts if p)
        return (letters or self.email[:2]).upper()


class SavedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_items")
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="saved_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "product")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.product}"


class AgeAttestation(models.Model):
    """Append-only audit log: a row per age attestation (ammo only). Never mutated."""

    CONTEXT_REGISTER = "register"
    CONTEXT_CHECKOUT = "checkout"
    CONTEXT_CHOICES = [
        (CONTEXT_REGISTER, "Registration"),
        (CONTEXT_CHECKOUT, "Checkout"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="age_attestations",
    )
    email = models.EmailField()
    context = models.CharField(max_length=16, choices=CONTEXT_CHOICES)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="age_attestations",
    )
    statement_version = models.CharField(max_length=16, default="v1")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    attested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attested_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["attested_at"]),
        ]

    def __str__(self):
        return f"{self.email} @ {self.attested_at:%Y-%m-%d %H:%M} ({self.context})"
