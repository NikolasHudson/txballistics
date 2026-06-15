import csv
import re
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Category, Product, ProductType

BULLET_PATTERNS = [
    ("Full Metal Jacket", "FMJ"),
    ("Hollow Point", "HP"),
    ("Soft Point", "SP"),
    ("Boat Tail Hollow Point", "BTHP"),
    ("Extreme Penetrator", "XP"),
    ("Ballistic Tip", "BT"),
    ("Lead Cast", "LC"),
    ("V-Max", "V-Max"),
    ("ELD-X", "ELD-X"),
    ("SST", "SST"),
    ("XTP", "XTP"),
    ("FTX", "FTX"),
]


def parse_grain(desc):
    m = re.search(r"(\d+)\s*gn", desc, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.match(r"\s*(\d{2,3})\b", desc)
    return int(m.group(1)) if m else None


def parse_bullet(desc):
    for needle, code in BULLET_PATTERNS:
        if needle.lower() in desc.lower():
            return code
    return ""


class Command(BaseCommand):
    help = "Import ammo products from data/ammo_pricing.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path", default=str(Path(settings.BASE_DIR) / "data" / "ammo_pricing.csv")
        )

    def handle(self, *args, **opts):
        path = Path(opts["path"])
        if not path.exists():
            self.stderr.write(f"CSV not found: {path}")
            return

        top_cache = {}
        sub_cache = {}
        created = updated = 0

        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                top_name = row["Category"].strip()
                cal = row["Caliber"].strip()
                title = row["Product"].strip()
                desc = row["Description"].strip()
                if not (top_name and cal and title):
                    continue

                # Top-level category
                if top_name not in top_cache:
                    top, _ = Category.objects.get_or_create(
                        slug=slugify(top_name),
                        defaults={"name": top_name, "product_type": ProductType.AMMO},
                    )
                    top_cache[top_name] = top
                top = top_cache[top_name]

                # Caliber sub-category
                if cal not in sub_cache:
                    sub, _ = Category.objects.get_or_create(
                        slug=slugify(cal),
                        defaults={
                            "name": cal, "parent": top,
                            "product_type": ProductType.AMMO,
                        },
                    )
                    sub_cache[cal] = sub
                sub = sub_cache[cal]

                price = Decimal(row["Cost"])
                rounds = int(row["RoundsPerBox"]) if row["RoundsPerBox"] else None
                grain = parse_grain(desc)
                bullet = parse_bullet(desc)
                usage = row["Usage"].strip()

                sku = slugify(title)[:60].upper()
                product, was_created = Product.objects.update_or_create(
                    sku=sku,
                    defaults={
                        "title": title,
                        "slug": slugify(title)[:280],
                        "category": sub,
                        "product_type": ProductType.AMMO,
                        "price": price,
                        "stock": 0,
                        "grain": grain,
                        "bullet_type": bullet,
                        "rounds_per_unit": rounds,
                        "use_type": usage,
                        "caliber_label": cal.split()[0][:12],
                        "is_active": True,
                    },
                )
                created += was_created
                updated += not was_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported pricing: {created} created, {updated} updated. "
                f"Categories: {len(top_cache)} top, {len(sub_cache)} calibers."
            )
        )
