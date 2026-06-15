"""Swappable payment provider interface.

v1 ships with ManualProvider (pay at pickup, no online charge). A compliance
payment partner can be added by implementing PaymentProvider and registering it
in PROVIDERS, then selecting it via SiteConfiguration.active_payment_provider.
"""
from apps.payments.models import Payment


class PaymentProvider:
    key = "base"
    label = "Base"

    def create_payment(self, order, request=None):
        raise NotImplementedError

    def confirm(self, payment, request=None):
        raise NotImplementedError

    def refund(self, payment, amount=None):
        raise NotImplementedError

    def handle_webhook(self, request):
        return None


class ManualProvider(PaymentProvider):
    key = "manual"
    label = "Pay at pickup"

    def create_payment(self, order, request=None):
        return Payment.objects.create(
            order=order,
            provider=self.key,
            amount=order.total,
            status=Payment.STATUS_PENDING,
        )

    def confirm(self, payment, request=None):
        # No online charge; remains pending until paid in person.
        return payment

    def refund(self, payment, amount=None):
        payment.status = Payment.STATUS_REFUNDED
        payment.save()
        return payment


PROVIDERS = {
    ManualProvider.key: ManualProvider(),
}


def get_active_provider():
    from apps.core.models import SiteConfiguration

    key = SiteConfiguration.get_solo().active_payment_provider
    return PROVIDERS.get(key, PROVIDERS["manual"])
