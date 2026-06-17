#!/usr/bin/env bash
set -e

echo "Waiting for database..."
python - <<'PY'
import os, time, sys
import dj_database_url
import psycopg2

url = os.environ.get("DATABASE_URL", "postgres://fursalink:fursalink@db:5432/fursalink")
cfg = dj_database_url.parse(url)
for attempt in range(30):
    try:
        psycopg2.connect(
            dbname=cfg["NAME"], user=cfg["USER"], password=cfg["PASSWORD"],
            host=cfg["HOST"], port=cfg["PORT"] or 5432,
        ).close()
        print("Database is ready.")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"  db not ready ({attempt+1}/30): {exc}")
        time.sleep(2)
else:
    print("Database never became available.")
    sys.exit(1)
PY

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
