# TX Ballistics

Django + HTMX storefront for a Central-Texas ammunition & fishing-tackle dealer, with a
[django-unfold](https://unfoldadmin.com/) back office. Ammo is **reserve-for-pickup**; fishing/tackle
is pickup now and **shipping-ready** behind a flag. See [`plan.md`](plan.md) for the full architecture.

## Stack
Django 5.1 · PostgreSQL · HTMX · django-unfold · django-solo · WhiteNoise · gunicorn

## Local development

```bash
# 1. Start Postgres (Docker)
docker compose up -d

# 2. Create a virtualenv and install deps
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Configure env (copy and tweak if needed)
cp .env.example .env

# 4. Migrate + seed demo data (imports the cleaned pricing sheet + fishing tackle)
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo

# 5. Create an admin user
DJANGO_SUPERUSER_PASSWORD=admin12345 .venv/bin/python manage.py createsuperuser \
    --noinput --email admin@txballistics.com

# 6. Run
.venv/bin/python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- Admin (Unfold): http://127.0.0.1:8000/admin/
- Demo customer: `travis.b@email.com` / `demo12345`

## Management commands
- `import_pricing` — load `data/ammo_pricing.csv` (handgun + rifle ammo).
- `seed_demo` — site config defaults, category tree, fishing tackle w/ color variants,
  testimonials, promo codes, a demo customer, and a hero deal.

## Back office (Site Configuration → the client's control panel)
Editable in the admin under **Settings → Site Configuration**:
- **Primary color** — recolors the storefront *and* the Unfold admin.
- **Catalog mode** — browse-only; disables all online ordering.
- **Show stock** — toggle stock counts/badges site-wide (default off).
- **Fishing shipping enabled** — flip tackle from pickup to shipping.
- Pickup address (revealed after ordering), store phone/email, guarantee copy, tax & shipping rates,
  active payment provider.

## Apps
`core` (config, home, about) · `catalog` (products/variants/specs, listing, search) ·
`accounts` (email-login user, saved items, **age-attestation audit**) · `cart` · `orders`
(checkout, atomic stock decrement, confirmation) · `payments` (swappable provider; `ManualProvider`
= pay at pickup) · `reviews` · `marketing` (testimonials, newsletter, restock alerts, promo codes).

## Deployment (DigitalOcean App Platform)
`.do/app.yaml` defines the web service + managed Postgres. Set `SECRET_KEY` and `SENDGRID_API_KEY`
as encrypted env vars. `Procfile` runs gunicorn; migrations run as a pre-deploy job.
Production settings: `config.settings.prod` (SendGrid SMTP email, security headers, WhiteNoise static).
