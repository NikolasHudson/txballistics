from .models import AgeAttestation


def record_attestation(request, *, email, context, order=None, user=None):
    """Append-only audit row, written every time a customer attests (ammo only)."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
    return AgeAttestation.objects.create(
        user=user if (user and user.is_authenticated) else None,
        email=email,
        context=context,
        order=order,
        ip_address=ip or None,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:400],
    )
