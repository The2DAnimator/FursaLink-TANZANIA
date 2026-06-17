# Deployment Guide — FursaLink Tanzania

This guide covers deploying FursaLink to a production environment. The app is
12-factor: all configuration comes from environment variables, and the same
Docker image runs everywhere.

## 1. Prerequisites

- A Linux host (or container platform) with Docker & Docker Compose, **or** a
  Python 3.12 runtime + PostgreSQL 14+ + Redis 6+.
- A PostgreSQL database and a Redis instance.
- A domain name and TLS certificate (via your load balancer / reverse proxy).

## 2. Environment variables

Copy `.env.example` to `.env` and set production values. The critical ones:

| Variable | Notes |
|----------|-------|
| `DJANGO_SETTINGS_MODULE` | Set to `config.settings.prod` |
| `DJANGO_SECRET_KEY` | Long random string — **required** |
| `DJANGO_DEBUG` | `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of your domains |
| `DATABASE_URL` | `postgres://USER:PASS@HOST:5432/DBNAME` |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | Redis URLs |
| `FRONTEND_URL` | Public base URL (used in verification/reset emails) |

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Optional integrations (mock until set)

Leave any of these blank to keep the corresponding feature in **mock mode**:

- Email: `SENDGRID_API_KEY` (or SMTP via `EMAIL_HOST*`)
- SMS / OTP: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`
- WhatsApp: `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_ID`
- Maps: `GOOGLE_MAPS_API_KEY`
- Payments: `STRIPE_SECRET_KEY`, `MPESA_*`, `AIRTEL_*`, `TIGO_API_KEY`
- External feeds: `TENDERS_FEED_URL`, `JOBS_FEED_URL`

## 3. Deploy with Docker Compose

```bash
git clone <repo-url> && cd fursalink-tanzania
cp .env.example .env        # edit for production
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
# optional demo data:
docker compose exec web python manage.py seed_data
```

The `entrypoint.sh` script waits for the database, runs migrations and
`collectstatic` automatically before Gunicorn starts. The compose file also
runs a Celery `worker` and `beat` scheduler.

Put a TLS-terminating reverse proxy (nginx, Caddy, or your cloud load balancer)
in front of the `web` service on port 8000.

## 4. Deploy without Docker

```bash
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.prod
# ... export the rest of your env vars ...

python manage.py migrate
python manage.py collectstatic --noinput

# Web (Gunicorn behind nginx)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Background workers (separate processes / systemd units)
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Static files are served by WhiteNoise from `STATIC_ROOT`; user uploads go to
`MEDIA_ROOT` — mount this on persistent storage (or use an S3-compatible
backend).

## 5. Scheduled jobs

Celery beat is preconfigured (`config/settings/base.py → CELERY_BEAT_SCHEDULE`):

- `collect_external_tenders` / `collect_external_jobs` — every 6h (no-op unless
  `TENDERS_FEED_URL` / `JOBS_FEED_URL` are set)
- `expire_advertisements` / `expire_subscriptions` — hourly
- `purge_old_audit_logs` — daily

## 6. Security checklist (prod settings)

`config.settings.prod` enables, and you should verify:

- `DEBUG = False`, correct `ALLOWED_HOSTS`
- `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` (1 year), HSTS subdomains/preload
- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- `X_FRAME_OPTIONS = "DENY"`
- Strong, secret `DJANGO_SECRET_KEY`
- Database and Redis not exposed publicly

Run Django's own audit:

```bash
python manage.py check --deploy
```

## 7. Health & smoke checks

```bash
curl -fsS https://your-domain/api/schema/ > /dev/null && echo "API up"
curl -fsS https://your-domain/ > /dev/null && echo "Frontend up"
```

## 8. Upgrades

```bash
git pull
docker compose up --build -d   # entrypoint re-runs migrations + collectstatic
```

Migrations are forward-only and safe to run on deploy.
