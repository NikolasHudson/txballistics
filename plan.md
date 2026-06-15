# TX Ballistics — Django Build Plan

Architecture and implementation plan for turning the static `mockup/` prototype into a
production Django app, with **Django Unfold** powering the admin/back office.

> This revision incorporates all decisions from review rounds 1–3. Decisions are baked into the body;
> **Section 18 ("Open Questions")** holds the little that's still outstanding.

---

## 0. Decisions Locked In

- **Fulfillment — pickup-only at launch, shipping-ready.** *Everything* (ammo **and** fishing) is
  **reserve-for-pickup** for now. The shipping machinery (address capture, rates) is **built but
  toggled off** behind a flag so the client can flip **fishing/tackle → shipping** themselves later
  without a code change. Fulfillment is a per-product field (defaulted by type) plus a
  `fishing_shipping_enabled` flag in Site Configuration.
- **No store selection.** Storefront runs from the owner's home. Customer orders, then the **pickup
  address is revealed after ordering** (confirmation page + email). Single pickup address, **editable
  in the backend.** (Confirmed: one address, no second location for v1.)
- **One order, split by product.** A cart/order can mix ammo + tackle; it stays **one order** but the
  line items are **grouped/split by fulfillment** in cart, checkout, confirmation, and admin.
- **No ID / DOB storage.** We never collect or store government IDs or birthdates. Customer presents a
  valid photo ID **and a matching name on the card used to order** at pickup. We keep only
  **age-attestation checkboxes**, and we **audit every attestation** (see Age Attestation Audit below).
- **Age attestation — ammo only**, and **audited**: every time a customer attests (at register and/or
  at each checkout containing ammo) we write an append-only `AgeAttestation` record (who/email,
  context, order ref, timestamp, IP, user agent).
- **Payments are pluggable** — a dedicated **`payments` app** with a swappable provider interface.
  **v1 ships with `ManualProvider`: no online charge — customer pays at pickup.** A compliance
  payment partner drops in later via the interface.
- **Catalog Mode flag** (backend) — when ON, the site is **browse-only**: no cart, checkout, or online
  ordering.
- **Stock display flag** (backend) — **defaults OFF** (no stock shown) for launch. Stock is still
  tracked internally and **only decremented when an order is placed** (never on add-to-cart).
- **Backend-editable branding** — primary color, **store phone & email**, and **guarantee copy** are
  all editable in Site Configuration. **The Unfold admin recolors from the same primary color**
  (confirmed supported — see §8).
- **Hero deal** — a **checkbox on the Product** in the admin marks it the homepage "Deal of the Day".
  Setting a new one **automatically replaces** the previous (only one hero at a time, enforced on save).
- **No bundling** — drop the "3 for $24 / mix & match" bundle feature entirely (copy + logic).
- **Remove all "tested" features** — no ammo "TESTED" badge, no fishing "TANK TESTED" badge, no
  lab-test / on-the-water test sections or models.
- **Listing view:** **table view only** for now (drop the card-grid listing).
- **Auth:** custom **email-login** user; **guest checkout allowed but email is required.**
- **Email only for v1** (no SMS), most likely via **SendGrid**.
- **Templates:** server-rendered Django + **HTMX**. CSS ported from mockup as-is.
- **Catalog scope:** keep **all categories as nav placeholders** (Handgun, Rifle, Shotgun, Rimfire,
  Bulk, Fishing…). Launch data = Handgun + Rifle (from the cleaned pricing sheet) + Fishing.
- **Brand/manufacturer optional** — ammo has none (house/reman); tackle has "Lone Star Lures".
- **Variants:** fishing lures have **per-color (variant-level) stock/SKU**.
- **DB:** PostgreSQL in **dev and prod** (local now; DO managed in prod). **Apps under `apps/`.
  Single admin role** for v1. **Hosting:** DigitalOcean **App Platform** + managed Postgres.

---

## 1. Product Overview

TX Ballistics is a Texas ammunition **and fishing-tackle** dealer.

- **Ammo** — reserve online, **pay at pickup** (address given after ordering). Attributes: caliber,
  grain, bullet type, casing, rounds/box, cost-per-round, usage, primer. No brand in the client data;
  "live, hand-counted" stock (display currently off).
- **Fishing/tackle** — same reserve-for-pickup flow **for now**; ready to switch to shipping later.
  Products have **color/pattern variants** (each its own SKU + stock) and a different spec set
  (lure type, length, weight, dive depth, hooks, line, target species).
- Shared marketing: homepage hero deal + weekly specials, rotating testimonials, newsletter, restock
  alerts, saved items, reviews, promo codes.

### Pages → route map

| Mockup file | Purpose | Django route (see §6) |
|---|---|---|
| `index.html` | Homepage: hero deal, categories, specials, testimonials, newsletter | `core:home` |
| `category-table.html` | Category listing — **table view (kept)** | `catalog:category` |
| `category-cards.html` | Card listing — **dropped for v1** (reference only) | — |
| `product.html` | Ammo product detail | `catalog:product_detail` (ammo template) |
| `lure-product.html` | Fishing product detail (variants/swatches) | `catalog:product_detail` (tackle template) |
| `cart.html` | Cart: line items (split by fulfillment), totals, promo | `cart:detail` |
| `checkout.html` | Checkout: contact, ammo age-attestation, payment | `orders:checkout` |
| `confirmation.html` | Order confirmed: **pickup address revealed**, what to bring, items | `orders:confirmation` |
| `account.html` | Account: dashboard, orders, saved items, profile, security | `accounts:dashboard` |
| `signin.html` | Sign in / register / guest | `accounts:login` / `accounts:register` |
| `about.html` | Static about/story page | `core:about` |

> **Mockup edits implied:** remove "TESTED"/"TANK TESTED" badges + test-data sections; remove
> store-selection block + DOB field from `checkout.html`; remove shipping/bundle copy from
> `lure-product.html` for now (keep behind the shipping flag); confirmation reveals the single pickup
> address.

---

## 2. Tech Stack

| Concern | Choice | Notes |
|---|---|---|
| Framework | Django 5.x, Python 3.12+ | |
| Admin | **django-unfold** | Themed; **primary color driven from `SiteConfiguration`** (§8) |
| DB (dev + prod) | **PostgreSQL** | Local now (docker-compose); DO managed in prod |
| Templates | Server-rendered Django + **HTMX** | `django-htmx` |
| CSS | Ported from `mockup/css/*` verbatim | + dynamic `--primary` color var |
| Config | `django-environ`, split settings | base/dev/prod |
| Auth | Custom `User` (email login) | guest checkout w/ required email |
| Payments | **`payments` app** w/ provider interface | `ManualProvider` (pay at pickup) in v1 |
| Email | **SendGrid** (`django-anymail` or SMTP) | email-only notifications |
| Images | `ImageField`, optional | **caliber/emoji text tile is the default**; image overrides |
| Singleton config | `django-solo` | the backend "settings" hub |
| Static (prod) | WhiteNoise | DO App Platform friendly |
| Tests | `pytest-django`, `factory_boy` | |

`requirements` sketch:
```
Django>=5.0
django-unfold
django-environ
django-htmx
django-solo
django-anymail[sendgrid]   # or plain SMTP to SendGrid
Pillow
psycopg[binary]
gunicorn
whitenoise
# stripe / partner-sdk     # added when the compliance provider is wired
pytest-django
factory_boy
```

---

## 3. Repository Structure

```
txballistics/
├── manage.py
├── requirements/ (base.txt dev.txt prod.txt)
├── .env.example
├── Procfile / runtime.txt / .do/app.yaml   # DO App Platform deploy
├── docker-compose.yml                        # local Postgres
├── data/ammo_pricing.csv                     # cleaned client pricing sheet (148 rows)
├── config/
│   ├── settings/ (base.py dev.py prod.py)
│   ├── urls.py  wsgi.py  asgi.py
│   └── unfold.py                             # UNFOLD callbacks: color, dashboard, badges
├── apps/
│   ├── core/        # base templates, home, about, SiteConfiguration, context processors, flags
│   ├── catalog/     # categories, manufacturers, products, variants, images, specs, search, CSV import
│   ├── reviews/     # product reviews
│   ├── accounts/    # custom User, profile, saved items, auth, dashboard, AgeAttestation audit
│   ├── cart/        # session+db cart (variant-aware)
│   ├── orders/      # orders, order items, checkout, confirmation (split by fulfillment)
│   ├── payments/    # swappable payment provider interface + Payment records
│   └── marketing/   # testimonials, newsletter, restock alerts, promo codes
├── templates/ (base.html, partials/, <app>/)
├── static/ (css/ js/ img/)
└── media/   # uploaded images (gitignored)
```

Each `AppConfig.name = "apps.<name>"`.

---

## 4. Apps — Detailed Breakdown

### 4.1 `core`
**`SiteConfiguration` (singleton, django-solo)** — the client's control panel:
- `primary_color` (hex) — injected as the storefront `--primary` CSS var **and** as the Unfold admin
  primary palette (§8).
- `catalog_mode` (bool) — browse-only when True.
- `show_stock` (bool, **default False**) — hide all stock UI when False.
- `fishing_shipping_enabled` (bool, **default False**) — when True, tackle products switch from
  pickup to shipping (enables shipping address + rates at checkout).
- `pickup_address`, `pickup_instructions` — revealed on confirmation + email.
- `store_phone`, `store_email` — editable; shown in header/footer/confirmation.
- `guarantee_copy` — editable marketing copy (the "$100 guarantee" text).
- `tax_rate` (default 0.0825), `shipping_flat_rate`, `free_shipping_threshold` — used only when
  shipping is enabled.
- `active_payment_provider` (choice — see `payments`).
- **Context processors:** `nav_categories`, `cart_summary`, `site_config` (flags, color, contact copy).
- **Views:** `home` (hero deal from `Product.is_hero_deal`, specials, testimonials, newsletter), `about`.
- `base.html` injects `:root{--primary: …}` from `SiteConfiguration`.

### 4.2 `catalog`  ← core of the app
**`Category`** — `name`, `slug*`, `parent` (self-FK), `product_type` (`ammo`|`tackle`), `blurb`,
`quick_facts`, `order`, `is_active`. Placeholders: Handgun, Rifle, Shotgun, Rimfire, Bulk, **Fishing**.
Sub-levels: calibers (9mm, 380 Auto, 308 Winchester…) and tackle types (Crankbaits, Soft Plastics…).

**`Manufacturer`** (optional) — `name`, `slug`, `short_name`, `is_house_brand`, `logo`.

**`Product`** (shared base for both types)
- Identity: `title*`, `slug*`, `sku*`, `category` FK, `manufacturer` FK (nullable),
  `product_type` (`ammo`|`tackle`), `fulfillment` (`pickup`|`ship`; defaults from type — tackle
  resolves to `ship` only when `fishing_shipping_enabled`).
- Commerce: `price`, `sale_price` (nullable), `stock`, `is_active`, `is_featured`, `is_special`,
  **`is_hero_deal`** (single-enforced: `save()`/admin unsets any other hero when set True).
- Display: `caliber_label` (tile text e.g. `9mm`, `🎣`), `image` (optional — shown only if set,
  else the text tile).
- **Ammo attributes** (nullable; power table columns + filters/sort): `grain`, `bullet_type`,
  `casing`, `rounds_per_unit`, `use_type` (Usage), `primer`, `muzzle_velocity`, `muzzle_energy`,
  `is_magnetic`.
- Content: `description`.
- **Derived:** `current_price`, `is_on_sale`, `savings`, `cost_per_round`, `in_stock`,
  `stock_status`, `avg_rating`, `review_count`, `total_stock`.

**`ProductVariant`** (fishing colors; per-color stock/SKU) — `product` FK, `name`, `sku_suffix`,
`swatch_color_1`, `swatch_color_2`, `stock`, `price_override` (nullable), `image` (optional),
`is_active`, `order`. Ammo has no variants. Cart/OrderItem reference a variant when present.

**`ProductImage`** — `product` FK, `variant` FK (nullable), `image`, `alt`, `order`.
**`ProductSpec`** — `product` FK, `label`, `value`, `order` (drives the spec table, esp. tackle).

**Views**
- `category(slug)` — **table listing**: filtering, sorting, pagination; columns adapt by
  `product_type`. Stock column/badges hidden when `show_stock` off; buy controls hidden in
  `catalog_mode`.
- `product_detail(slug)` — ammo vs tackle template by type; tackle renders swatch picker bound to
  variants. Reviews + related in both.
- `search` — title/sku/caliber/manufacturer (Postgres full-text in prod).

**Management commands**
- `import_pricing` — loads **`data/ammo_pricing.csv`** (already cleaned: separators/dupes removed,
  typos fixed, `Category` column = Handgun/Rifle, cost-per-round recomputed). Maps `Category`→top
  category, `Caliber`→sub-category, parses `grain`/`bullet_type` from `Description`, `Cost`→price,
  `RoundsPerBox`→rounds_per_unit, `Usage`→use_type. New ammo defaults to `stock=0` (hidden anyway,
  since `show_stock` is off).
- `seed_demo` — category tree (incl. Fishing → Crankbaits/Soft Plastics/Topwater), a few tackle
  products **with color variants**, testimonials, demo customer + order history, promo codes,
  `SiteConfiguration` defaults.

**Admin (Unfold):** Product list (title, category, type, price/sale, stock badge, active, featured,
hero); `is_hero_deal` checkbox enforcing single hero; inlines for Variant/Image/Spec; bulk actions
(feature/special, adjust stock, activate). Category tree; Manufacturer.

### 4.3 `reviews`
- `Review` — `product` FK, `author` (User, nullable), `display_name`, `rating` (1–5), `body`,
  `is_verified`, `created_at`, `is_approved`. Submit form + admin moderation. (No "tested" concept.)

### 4.4 `accounts`
- **Custom `User`** (`AbstractUser`, `USERNAME_FIELD="email"`): `email*`, `first_name`, `last_name`,
  `phone`, `member_since`, `customer_tier`, comms prefs (`notify_pickup_email`,
  `notify_restock_email`, `notify_weekly_deals`). **No DOB, no ID fields.**
- `SavedItem` — `user` FK, `product` FK, `created_at`.
- **`AgeAttestation` (append-only audit)** — `user` FK (nullable for guests), `email`, `context`
  (`register`|`checkout`), `order` FK (nullable), `attested_at`, `ip_address`, `user_agent`,
  `statement_version`. A new row is written **every time** a customer ticks the age attestation;
  records are never updated/deleted. Surfaced read-only in the admin for compliance.
- **Views:** login, logout, register (email + ammo age-attestation), dashboard tabs, profile update,
  password change, guest passthrough. Dashboard stats = aggregates.

### 4.5 `cart`
- Session cart for guests, DB cart for users; **merge on login**.
- `Cart` — `user`/`session_key` (nullable). `CartItem` — `cart` FK, `product` FK, `variant` FK
  (nullable), `quantity`.
- **Services:** add/update/remove, merge, `totals()` → subtotal, discount (promo), tax, shipping
  (only when shipping enabled + tackle present), grand total. Cart UI **groups lines by fulfillment**
  (pickup vs ship).
- **HTMX endpoints** return updated cart partial + OOB header badge. All disabled in `catalog_mode`.

### 4.6 `orders`
- `Order` — `number*` (`TX-#####`), `user` (nullable), contact snapshot (incl. **required email**),
  `has_pickup_items`/`has_ship_items` (derived), shipping address fields (used only when shipping
  enabled), `status` (`reserved`→`ready`/`shipped`→`picked_up`/`completed`/`cancelled`),
  `payment_method`, `payment_status`, `subtotal`, `discount`, `tax`, `shipping`, `total`,
  `promo_code` FK (nullable), timestamps.
- `OrderItem` — `order` FK, `product` FK (SET_NULL), **snapshot** (`title`, `sku`, `variant_name`,
  `caliber_label`, `unit_price`, `quantity`, **`fulfillment`**). One order; items grouped by
  fulfillment everywhere.
- **Checkout:** contact always; **age attestation only when cart contains ammo** (writes an
  `AgeAttestation` row); shipping address only if shipping enabled + tackle present; payment via
  active provider (`ManualProvider` → pay at pickup). POST validates, creates Order+items,
  **atomically decrements stock** (per-variant for tackle), records `Payment`, clears cart →
  confirmation. **Blocked in `catalog_mode`.**
- **Confirmation:** **reveals the pickup address** + "what to bring" (photo ID + **matching card
  name**); shipping section only when shipping used. Owner/session-guarded.
- **Admin (Unfold):** order list + status workflow actions; items inline (readonly snapshot, grouped);
  filters by status/date/fulfillment.

### 4.7 `payments` (swappable)
- **`PaymentProvider` interface:** `create_payment(order)`, `confirm`, `capture`, `refund`,
  `handle_webhook(request)`, `label`. Selected via `SiteConfiguration.active_payment_provider`.
- **`ManualProvider` (v1 default):** records the order as reserved, **payment due at pickup** — no
  online charge, no PCI scope. Lets us launch before the compliance partner is signed.
- **`StripeProvider`/`PartnerProvider` (stubs):** drop-in later; card name captured here feeds the
  pickup ID-match.
- **`Payment`** — `order` FK, `provider`, `amount`, `status`, `external_ref`, `card_last4`, `created_at`.

### 4.8 `marketing`
- `Testimonial` — `quote`, `author`, `rating`, `is_active`, `order`.
- `NewsletterSubscriber` — `email*`, `is_active`, `created_at`.
- `RestockAlert` — `email`/`user`, `product` FK, `variant` FK (nullable), `notified_at` (email-only).
- `PromoCode` — `code*`, `kind` (`percent`|`fixed`), `value`, `active`, `starts/ends`,
  `min_subtotal`, `usage_limit`, `used_count`. **Client-creatable in admin**; **% or fixed-dollar**;
  computed at checkout (applied to subtotal before tax).

---

## 5. Data Model Summary

```
SiteConfiguration (singleton: color, flags, pickup addr, phone/email, guarantee, tax, shipping, provider)

Category ─ self.parent, product_type
   └─< Product (product_type, fulfillment, is_hero_deal) ── Manufacturer (optional)
          ├─< ProductVariant (per-color stock/sku)        ← tackle
          ├─< ProductImage / ProductSpec
          ├─< Review / SavedItem / RestockAlert ── User
          ├─< CartItem (── variant) ── Cart ── User/session
          └─< OrderItem (snapshot + variant_name + fulfillment) ── Order
Order ── User (nullable) ── PromoCode (nullable) ──1 Payment ── provider
User ─< AgeAttestation (append-only audit) ── Order (nullable)
Testimonial / NewsletterSubscriber (standalone)
```

---

## 6. URL Map

```
/                          core:home
/about/                    core:about
/search/                   catalog:search
/c/<category-slug>/        catalog:category            (table view; filters/sort via querystring)
/p/<product-slug>/         catalog:product_detail      (ammo or tackle template)
/p/<slug>/review/          reviews:create

/cart/                     cart:detail                 (disabled in catalog_mode)
/cart/add|update|remove/   cart:*  (POST/HTMX)
/checkout/                 orders:checkout             (disabled in catalog_mode)
/order/<number>/          orders:confirmation
/payments/webhook/<provider>/   payments:webhook

/account/                  accounts:dashboard          (?tab=orders|saved|profile|security)
/account/login|register|logout/
/account/saved/toggle/     accounts:save_toggle  (HTMX)

/newsletter/subscribe/     marketing:subscribe   (HTMX)
/restock/notify/           marketing:restock_notify (HTMX)
/promo/apply/              marketing:promo_apply (HTMX)

/admin/                    Unfold admin
```

---

## 7. Frontend Strategy

1. `base.html`: head/fonts/CSS, two-tier header (with **Fishing** nav), footer (phone/email/guarantee
   from `SiteConfiguration`), blocks, and the dynamic `--primary` `<style>`.
2. Partials: `_utility_bar`, `_primary_nav`, `_breadcrumb`, `_footer`, `_product_row` (table),
   `_pagination`, `_order_summary`, `_cart_item`, `_swatch_picker` (tackle).
3. CSS copied verbatim (incl. `lure-product.css`); swap hardcoded green for `var(--primary)`.
4. JS: keep testimonials rotator, qty/total, swatch picker (bound to variant data), account/auth tabs;
   move cart math to **HTMX** (server authoritative); drop `category.js` rendering (server renders).
5. Flag-aware rendering: `site_config.show_stock` (stock UI), `site_config.catalog_mode` (hide buy/cart).
6. Default product visual = caliber/emoji **text tile**; render `image` only when uploaded.

---

## 8. Django Unfold — Back Office (researched, implementation-ready)

**Install:** `pip install django-unfold`. In `INSTALLED_APPS`, `unfold` and any `unfold.contrib.*`
(`filters`, `forms`, `inlines`, `import_export`…) must come **before** `django.contrib.admin`. No extra
middleware required.

**Primary color from the DB (confirmed supported).** Unfold resolves any `UNFOLD` value that is a
**dotted-path string or callable(request)** on each request; `COLORS["primary"]` may be a callable
returning the 50–950 shade dict. So we point it at a callback that reads `SiteConfiguration`:

```python
# config/unfold.py
def primary_palette(request):
    from apps.core.models import SiteConfiguration
    base = SiteConfiguration.get_solo().primary_color   # hex like "#2f5d3a"
    # v1: same hex across weights (flat). Later: generate a real 50–950 ramp.
    return {str(w): base for w in (50,100,200,300,400,500,600,700,800,900,950)}

def dashboard_callback(request, context):
    from apps.orders.models import Order
    context["kpi"] = [...]            # awaiting pickup, low stock, today's orders, revenue
    return context
```

```python
# settings/base.py
UNFOLD = {
    "SITE_TITLE": "TX Ballistics Admin",
    "SITE_HEADER": "TX Ballistics",
    "SITE_SYMBOL": "store",
    "DASHBOARD_CALLBACK": "config.unfold.dashboard_callback",
    "COLORS": {"primary": "config.unfold.primary_palette"},   # ← DB-driven brand color
    "SIDEBAR": {
        "navigation": [
            {"title": "Catalog", "separator": True, "items": [
                {"title": "Products", "icon": "inventory_2",
                 "link": "{% raw %}{% url 'admin:catalog_product_changelist' %}{% endraw %}"},
                {"title": "Categories", "icon": "category", "link": "..."},
                {"title": "Manufacturers", "icon": "factory", "link": "..."},
            ]},
            {"title": "Sales", "separator": True, "items": [
                {"title": "Orders", "icon": "receipt_long", "link": "..."},
                {"title": "Payments", "icon": "payments", "link": "..."},
                {"title": "Promo Codes", "icon": "sell", "link": "..."},
            ]},
            {"title": "Customers", "items": [
                {"title": "Users", "icon": "person", "link": "..."},
                {"title": "Reviews", "icon": "star", "link": "..."},
                {"title": "Age Attestations", "icon": "verified_user", "link": "..."},
            ]},
            {"title": "Marketing", "items": [
                {"title": "Testimonials", "icon": "format_quote", "link": "..."},
                {"title": "Newsletter", "icon": "mail", "link": "..."},
                {"title": "Restock Alerts", "icon": "notifications", "link": "..."},
            ]},
            {"title": "Settings", "items": [
                {"title": "Site Configuration", "icon": "settings", "link": "..."},
            ]},
        ],
    },
}
```

**Admin code:** subclass `unfold.admin.ModelAdmin`; use `unfold.admin.TabularInline/StackedInline`
for Variant/Image/Spec/OrderItem inlines; colored status pills via `@unfold.decorators.display(label=…)`;
order workflow buttons via `@unfold.decorators.action` (`actions_list`/`actions_detail`,
`variant=ActionVariant.SUCCESS|DANGER`). KPI dashboard via `DASHBOARD_CALLBACK` + a custom
`templates/admin/index.html`.

> Caveat from research: the innermost color *weight* value isn't itself re-resolved as a callable, so
> dynamic color must come from the `COLORS["primary"]` callback (the palette level), as above. The
> callback runs per request — keep `get_solo()` cheap / cached. Icons are **Material Symbols** names.

---

## 9. Inventory, Fulfillment & Flags

- **Stock authoritative** on `Product.stock` / `ProductVariant.stock`. Decrement only at order
  placement, inside `transaction.atomic()` with a guarded `F()` update (`stock__gte=qty`); roll back +
  "only N left" on failure.
- **`show_stock` (default OFF):** hides all stock UI; internal tracking/decrement still runs.
- **`catalog_mode`:** disables all ordering (UI + endpoints) — browse-only.
- **`fishing_shipping_enabled` (default OFF):** when ON, tackle `fulfillment` resolves to `ship` and
  checkout collects a shipping address + applies flat/free-over-threshold shipping. Until then,
  everything is pickup and the shipping UI stays hidden.
- **Mixed cart = one order, split by fulfillment** in totals, checkout, confirmation, admin.

---

## 10. Auth, Accounts & Compliance

- Email login; "keep me signed in" toggles session expiry. **Guest checkout with required email.**
- **No ID/DOB stored.** Only **age-attestation checkboxes (ammo)**, and **every attestation is
  audited** in `AgeAttestation` (timestamp, IP, UA, context, order). Pickup verification = photo ID +
  matching card name (operational, once a real card provider is live).
- Password reset via Django's built-in email flow (SendGrid).

---

## 11. Seed / Import Data

- **`data/ammo_pricing.csv`** — the client's sheet, **already cleaned**: blank separator rows + exact
  duplicates removed, typos fixed (Huntion→Hunting, tripple→triple), calibers trimmed, a `Category`
  (Handgun/Rifle) column added, cost-per-round recomputed. 148 rows (48 handgun, 100 rifle, 32
  calibers). Original file left untouched as the source of record.
- `import_pricing` loads it; `seed_demo` adds the Fishing tree + tackle variants, testimonials, a demo
  customer/order, promo codes, and `SiteConfiguration` defaults.

---

## 12. Settings, Environment & Deployment (DigitalOcean App Platform)

- Split settings (`base`/`dev`/`prod`); `django-environ`.
- **Local dev Postgres** via `docker-compose.yml` (`postgres:16`).
- **Prod on DO App Platform:** `gunicorn config.wsgi`, WhiteNoise static, **DO managed Postgres** via
  `DATABASE_URL`; `.do/app.yaml` defines the web service, env vars, and a pre-deploy job
  (`migrate` + `collectstatic`).
- **Email via SendGrid** (`django-anymail` or SMTP) — order/pickup/restock notifications.
- `.env`: `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
  `SENDGRID_API_KEY`, payment provider keys (later).

---

## 13. Build Phases

1. **Scaffold** — project, split settings, **local Postgres**, custom User, Unfold themed +
   **DB-driven color**, `SiteConfiguration` + flags + dynamic CSS color, `base.html`/partials, port
   CSS/JS, static pipeline, DO deploy skeleton, SendGrid email backend.
2. **Catalog read path** — models + admin, `import_pricing` + `seed_demo`, **table listing**
   (flag-aware), ammo & tackle detail templates (swatch picker), search, hero-deal homepage.
3. **Cart** — services (variant-aware, promo/tax/shipping, mixed split), HTMX add/update/remove,
   badge, catalog-mode guards.
4. **Accounts** — email auth, register w/ attestation, dashboard tabs, profile, saved items,
   `AgeAttestation` audit.
5. **Orders + payments** — checkout (conditional shipping, ammo attestation → audit), atomic stock
   decrement, `payments` interface + `ManualProvider` + `Payment`, confirmation (address reveal),
   order history, Unfold workflow, promo computation.
6. **Marketing & reviews** — testimonials, newsletter, restock alerts (email), promo admin, reviews +
   moderation.
7. **Polish** — email notifications, tests, security headers, DO production cutover.

---

## 14. Risks / Watch-list

- **Overselling** → atomic, variant-aware decrement is mandatory.
- **Order immutability** → snapshot product/variant fields on `OrderItem`.
- **Shipping toggle** → keep shipping code paths complete-but-dormant so the client's flag flip "just
  works"; test both states.
- **Payment swap** → keep the provider interface clean so the partner drops in without touching
  checkout/order code.
- **Attestation audit** → append-only; never mutate; index by email/user for compliance lookups.
- **Dynamic admin color** → per-request callback; cache `get_solo()`.

---

## 18. Open Questions (small / remaining)

1. **SendGrid:** confirm SendGrid and provide (later) an API key + verified sender domain. OK to wire
   `django-anymail[sendgrid]`?
2. **Shipping values (for when the flag is flipped):** confirm flat rate + free-over threshold (mockup
   implied free over $35) so the dormant logic has correct defaults.
3. **Compliance payment partner:** name/SDK when known, so I can shape the provider stub + webhook.
4. **Fishing seed data:** the only tackle in the mockup is the squarebill crankbait (+ 4 related). OK
   for me to seed a small representative tackle set (with color variants) as demo, for you to replace?
5. **Grain spacing:** a few product names read "115 gn" (with a space). The importer will parse these
   fine; want me to also normalize the stored names to "115gn", or leave names exactly as the client
   wrote them?
</content>
</invoke>
