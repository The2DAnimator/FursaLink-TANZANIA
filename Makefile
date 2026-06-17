.PHONY: help install migrate run seed test lint format schema worker beat docker-up docker-down

help:
	@echo "FursaLink Tanzania — common commands"
	@echo "  make install     Install Python dependencies"
	@echo "  make migrate     Apply database migrations"
	@echo "  make run         Run the dev server"
	@echo "  make seed        Load demo data"
	@echo "  make test        Run the test suite"
	@echo "  make lint        Run ruff lint checks"
	@echo "  make format      Auto-format with ruff"
	@echo "  make schema      Export the OpenAPI schema to schema.yml"
	@echo "  make worker      Run a Celery worker"
	@echo "  make beat        Run the Celery beat scheduler"
	@echo "  make docker-up   Start the full stack with docker compose"

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8000

seed:
	python manage.py seed_data

test:
	DJANGO_SETTINGS_MODULE=config.settings.test pytest

lint:
	ruff check .

format:
	ruff check --fix . && ruff format .

schema:
	python manage.py spectacular --file schema.yml

worker:
	celery -A config worker -l info

beat:
	celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

docker-up:
	docker compose up --build

docker-down:
	docker compose down
