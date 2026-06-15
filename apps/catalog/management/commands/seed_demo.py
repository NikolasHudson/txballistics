from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import (
    Category, Manufacturer, Product, ProductSpec, ProductType, ProductVariant,
)
from apps.core.models import SiteConfiguration
from apps.marketing.models import PromoCode, Testimonial
from apps.reviews.models import Review

User = get_user_model()

PLACEHOLDER_TOPS = [
    ("Handgun", ProductType.AMMO, "9mm · .45 ACP · .380 · .40 S&W"),
    ("Rifle", ProductType.AMMO, "5.56 · .223 · .308 · 6.5 CM"),
    ("Shotgun", ProductType.AMMO, "12ga · 20ga · 410 · Buckshot"),
    ("Rimfire", ProductType.AMMO, ".22 LR · .22 WMR · .17 HMR"),
    ("Bulk", ProductType.AMMO, "500 / 1000 round value packs"),
    ("Fishing", ProductType.TACKLE, "Crankbaits · Soft Plastics · Topwater"),
]

TACKLE_SUBS = ["Crankbaits", "Soft Plastics", "Topwater", "Spinnerbaits"]

TESTIMONIALS = [
    ("Reserved Thursday, picked it up Saturday morning. Counts were exactly right and they had it bagged and ready. This is my shop now.", "Dale R., Round Rock"),
    ("Finally a dealer that actually has what the site says they have. No backorder games.", "Marisol T., San Antonio"),
    ("Grabbed a case of 5.56 for a training class. Best price I found and it was waiting at the counter.", "Coach Vance, Killeen"),
    ("Called with a dumb question about grain weight and they spent ten minutes helping. Real people.", "Jenny K., Waco"),
]

LURE_COLORS = [
    ("Chartreuse Shad", "#d8e23a", "#3a7d44"),
    ("Texas Craw", "#8a3b1e", "#c8551b"),
    ("Bluegill", "#2c6e8f", "#7fae3a"),
    ("Sexy Shad", "#cfd6da", "#3b5d8a"),
    ("Black/Chrome", "#cfd2d4", "#1c1c1a"),
]


class Command(BaseCommand):
    help = "Seed demo data (config, categories, fishing tackle, testimonials, promos, demo user)."

    def handle(self, *args, **opts):
        # Site config defaults
        cfg = SiteConfiguration.get_solo()
        cfg.save()
        self.stdout.write("Site configuration ready.")

        # Ammo products + caliber categories from the cleaned CSV
        call_command("import_pricing")

        # Placeholder top-level categories (keep all in nav)
        tops = {}
        for i, (name, ptype, blurb) in enumerate(PLACEHOLDER_TOPS):
            cat, _ = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "product_type": ptype, "blurb": blurb, "order": i},
            )
            cat.blurb = blurb
            cat.order = i
            cat.product_type = ptype
            cat.save()
            tops[name] = cat

        # Fishing subcategories
        fishing = tops["Fishing"]
        fsubs = {}
        for j, name in enumerate(TACKLE_SUBS):
            sub, _ = Category.objects.get_or_create(
                slug=slugify("fishing-" + name),
                defaults={
                    "name": name, "parent": fishing,
                    "product_type": ProductType.TACKLE, "order": j,
                },
            )
            fsubs[name] = sub

        house, _ = Manufacturer.objects.get_or_create(
            slug="lone-star-lures",
            defaults={"name": "Lone Star Lures", "short_name": "LSL", "is_house_brand": True},
        )

        # A representative tackle product with color variants
        crank, _ = Product.objects.get_or_create(
            sku="LSL-SQB-25",
            defaults={
                "title": "Hill Country Squarebill Crankbait — 2.5\"",
                "slug": "hill-country-squarebill-crankbait-25",
                "category": fsubs["Crankbaits"],
                "manufacturer": house,
                "product_type": ProductType.TACKLE,
                "price": Decimal("11.99"),
                "sale_price": Decimal("8.99"),
                "caliber_label": "🎣",
                "is_active": True,
                "is_featured": True,
                "is_special": True,
                "description": "The Hill Country Squarebill is built to deflect off rock, "
                "laydowns, and dock pilings to trigger reaction strikes from shallow Texas bass.",
            },
        )
        specs = [
            ("Lure Type", "Squarebill Crankbait (shallow)"),
            ("Length", "2.5 in (64 mm)"),
            ("Weight", "1/2 oz (14 g)"),
            ("Dive Depth", "2–5 ft"),
            ("Hooks", "2 × #4 VMC round-bend trebles"),
            ("Best Line", "10–14 lb fluorocarbon"),
            ("Target Species", "Largemouth, smallmouth, spotted bass"),
        ]
        if not crank.specs.exists():
            for k, (label, value) in enumerate(specs):
                ProductSpec.objects.create(product=crank, label=label, value=value, order=k)
        if not crank.variants.exists():
            for k, (name, c1, c2) in enumerate(LURE_COLORS):
                ProductVariant.objects.create(
                    product=crank, name=name, sku_suffix=slugify(name)[:12].upper(),
                    swatch_color_1=c1, swatch_color_2=c2, stock=20 + k, order=k,
                )

        # A few more tackle items so Fishing isn't a one-product category
        extra_tackle = [
            ("Lone Star Soft Plastic Worm — 7\" — 8 pack", "Soft Plastics", "5.49", "🪱"),
            ("Topwater Walking Bait — 4.5\" — Bone", "Topwater", "10.99", "🌊"),
            ("Texas Spinnerbait — 3/8 oz — Chartreuse/White", "Spinnerbaits", "6.99", "🥄"),
        ]
        for title, subname, price, label in extra_tackle:
            Product.objects.get_or_create(
                sku=slugify(title)[:60].upper(),
                defaults={
                    "title": title, "slug": slugify(title)[:280],
                    "category": fsubs[subname], "manufacturer": house,
                    "product_type": ProductType.TACKLE, "price": Decimal(price),
                    "caliber_label": label, "is_active": True,
                },
            )

        # Hero deal + specials from ammo
        cheap_9mm = (
            Product.objects.filter(product_type=ProductType.AMMO, category__name__iexact="9mm")
            .order_by("price")
            .first()
        )
        if cheap_9mm:
            cheap_9mm.is_hero_deal = True
            cheap_9mm.sale_price = (cheap_9mm.price * Decimal("0.9")).quantize(Decimal("0.01"))
            cheap_9mm.is_special = True
            cheap_9mm.save()

        for p in Product.objects.filter(product_type=ProductType.AMMO).order_by("-price")[:4]:
            p.is_special = True
            p.save()

        # Testimonials
        for i, (quote, author) in enumerate(TESTIMONIALS):
            Testimonial.objects.get_or_create(
                author=author, defaults={"quote": quote, "order": i}
            )

        # Promo codes
        PromoCode.objects.get_or_create(
            code="RANGE10", defaults={"kind": "percent", "value": Decimal("10")}
        )
        PromoCode.objects.get_or_create(
            code="TX5OFF", defaults={"kind": "fixed", "value": Decimal("5"), "min_subtotal": Decimal("50")}
        )

        # Demo customer
        if not User.objects.filter(email="travis.b@email.com").exists():
            u = User.objects.create_user(
                email="travis.b@email.com", password="demo12345",
                first_name="Travis", last_name="Bishop", phone="(512) 555-0142",
                customer_tier="Gold",
            )
            self.stdout.write(f"Demo customer: {u.email} / demo12345")

        # A couple approved reviews on the hero
        if cheap_9mm and not cheap_9mm.reviews.exists():
            Review.objects.create(
                product=cheap_9mm, display_name="Travis B.", rating=5, is_approved=True,
                is_verified=True,
                body="Runs flawless in my Glock 19. Best 9mm price in the Hill Country.",
            )
            Review.objects.create(
                product=cheap_9mm, display_name="Dana R.", rating=5, is_approved=True,
                is_verified=True,
                body="Clean burning and the counts were dead-on. My go-to range load now.",
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
