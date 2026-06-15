from django import forms


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80)
    email = forms.EmailField()
    phone = forms.CharField(max_length=32, required=False)
    notify_when_ready = forms.BooleanField(required=False, initial=True)

    # Shipping (only required when the cart has shippable items)
    ship_street = forms.CharField(max_length=200, required=False)
    ship_city = forms.CharField(max_length=80, required=False)
    ship_state = forms.CharField(max_length=2, required=False)
    ship_zip = forms.CharField(max_length=10, required=False)

    # Age attestations (only required when the cart has ammo)
    age_attest = forms.BooleanField(required=False)
    not_prohibited_attest = forms.BooleanField(required=False)

    payment_method = forms.ChoiceField(
        choices=[("pay_at_pickup", "Pay at pickup")],
        initial="pay_at_pickup",
    )

    def __init__(self, *args, needs_shipping=False, needs_age=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.needs_shipping = needs_shipping
        self.needs_age = needs_age

    def clean(self):
        cleaned = super().clean()
        if self.needs_shipping:
            for f in ["ship_street", "ship_city", "ship_state", "ship_zip"]:
                if not cleaned.get(f):
                    self.add_error(f, "Required for shipped items.")
        if self.needs_age:
            if not cleaned.get("age_attest"):
                self.add_error("age_attest", "You must confirm you meet the age requirement.")
            if not cleaned.get("not_prohibited_attest"):
                self.add_error(
                    "not_prohibited_attest",
                    "You must confirm you are not prohibited from purchasing.",
                )
        return cleaned
