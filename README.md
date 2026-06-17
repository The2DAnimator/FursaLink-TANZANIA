# FursaLink Tanzania

**The business opportunity and market intelligence platform for Tanzania.**

FursaLink connects businesses, entrepreneurs, farmers, traders, job seekers,
suppliers, buyers and investors with verified opportunities, market prices,
tenders and jobs across Tanzania. The platform **never sells phone numbers** —
people and businesses connect through a secure, permission-based system.

Built with **Django 5 + Django REST Framework + PostgreSQL**, a JWT-secured
API-first backend, a Bootstrap 5 frontend, Celery/Redis background jobs and
pluggable integrations for payments, SMS, WhatsApp, email and maps.

---

## Features

| # | Module | Highlights |
|---|--------|-----------|
| 1 | Business Directory | Search, filters, verification, featured listings, reviews & ratings |
| 2 | Product Marketplace | Categories, images, stock tracking, price & region filters |
| 3 | Market Opportunities | Supply / buyer / investment / partnership / distribution posts |
| 4 | Tenders | Government / NGO / private + external feed collection |
| 5 | Job Portal | Listings, internships, freelance, applications with CV upload |
| 6 | Market Price Intelligence | Crops, livestock, materials, fuel, electronics — trends & regional comparison |
| 7 | Buyer–Seller Matching | TF-IDF/ML recommendations with keyword fallback |
| 8 | Lead Generation | Permission-based leads with transparent scoring |
| 9 | Advertising | Featured listings, homepage / banner ads, sponsored opportunities |
| 10 | Notifications | In-app, email, SMS, WhatsApp with per-user preferences |
| 11 | Analytics | Business/product views, leads, applications, revenue, user growth (Chart.js) |

**Cross-cutting:** custom email-based User with 5 roles (Super Admin, Business
Owner, Buyer, Seller, Job Seeker), RBAC permissions, audit logging of all
mutations, email verification, password reset, rate limiting, subscription
plans (Free / Standard / Premium) and payments (M-Pesa, Airtel Money, Tigo
Pesa, Stripe).

### Mock-first integrations

Every third-party integration (SendGrid, Twilio, WhatsApp, Google Maps, and all
payment gateways) is implemented behind a service abstraction. When the relevant
API keys are **absent**, the service returns deterministic mock responses, so the
entire platform runs end-to-end in development and CI **without any external
accounts**. Drop real credentials into `.env` to go live — no code changes needed.

---

## Tech stack

- Python 3.12+, Django 5.1, Django REST Framework, SimpleJWT
- PostgreSQL (SQLite for tests), Redis + Celery (worker & beat)
- drf-spectacular (OpenAPI 3 / Swagger UI / ReDoc)
- Bootstrap 5, vanilla JS (Fetch API), Chart.js
- scikit-learn (optional) for matching; graceful keyword fallback
- Docker + docker-compose, Gunicorn, WhiteNoise
- pytest + pytest-django, ruff

---

## Quick start (local)

```bash
# 1. Clone & enter
cd fursalink-tanzania

# 2. Create a virtualenv and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env          # tweak as needed

# 4. Create the database (PostgreSQL) — or use the Docker option below
#    Then run migrations + load demo data
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
python manage.py seed_data

# 5. Run it
python manage.py runserver
```

Visit:

- Frontend: <http://localhost:8000/>
- Swagger UI: <http://localhost:8000/api/docs/>
- ReDoc: <http://localhost:8000/api/redoc/>
- Django admin: <http://localhost:8000/admin/>

Seeded logins:

- **Admin:** `admin@fursalink.co.tz` / `admin12345`
- **Demo users:** `owner1@…`, `seller1@…`, `buyer1@…`, `jobseeker1@…` (all `password123`)

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
# then, in another shell:
docker compose exec web python manage.py seed_data
```

This brings up Postgres, Redis, the web app (Gunicorn), a Celery worker and a
Celery beat scheduler.

---

## Project layout

```
config/                 Project config
  settings/             base / dev / prod / test split
  urls.py, api_urls.py  Frontend + versioned API routing (/api/v1/)
  celery.py             Celery app + beat schedule
apps/
  core/                 Base models, RBAC, audit middleware, seed_data command
  accounts/             Custom User, JWT auth, email verify, password reset
  businesses/           Directory, reviews, verification, featured
  products/             Marketplace + inventory + images
  opportunities/        Market opportunities
  tenders/              Tenders + external feed task
  jobs/                 Jobs + applications + external feed task
  marketprices/         Price intelligence + trends/regional endpoints
  matching/             TF-IDF matching engine + spam detection
  leads/                Lead generation + scoring signals
  advertising/          Ad plans + advertisements
  notifications/        Multi-channel notifications + preferences
  subscriptions/        Plans, subscriptions, payments + checkout
  analytics/            Dashboard metric endpoints
  integrations/         email / sms / whatsapp / maps / payments services
templates/              Bootstrap 5 pages
static/                 CSS + JS (API client, listings, charts)
tests/                  pytest suite
```

---

## API

All endpoints are versioned under `/api/v1/`. Authentication is JWT:

```bash
# Obtain tokens
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@fursalink.co.tz","password":"admin12345"}'

# Use the access token
curl http://localhost:8000/api/v1/analytics/overview/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

The full, always-up-to-date contract is the OpenAPI schema at `/api/schema/`
(rendered at `/api/docs/`).

---

## Testing & quality

```bash
make test     # pytest (uses config.settings.test, in-memory SQLite)
make lint     # ruff
make schema   # export OpenAPI schema to schema.yml
```

CI (GitHub Actions) runs ruff, `manage.py check`, a migration completeness
check, OpenAPI validation and the test suite on every push/PR.

---

## Deployment

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for a production deployment guide
(environment variables, PostgreSQL/Redis, Gunicorn, Celery, static/media,
security hardening and going live with real integration credentials).

## Security

JWT auth, role-based access control, CSRF protection, request throttling, input
validation, audit logging of every mutation, email verification and password
reset are built in. Production settings (`config.settings.prod`) enable SSL
redirect, HSTS, secure cookies and `X-Frame-Options: DENY`.
