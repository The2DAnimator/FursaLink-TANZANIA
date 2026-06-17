"""Collect jobs from an external JSON feed and dispatch job alerts."""
import logging

import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def collect_external_jobs():
    url = settings.EXTERNAL_FEEDS.get("JOBS_FEED_URL")
    if not url:
        logger.info("JOBS_FEED_URL not configured; skipping job collection")
        return {"status": "skipped"}

    from apps.jobs.models import Job

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        items = resp.json()
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("Failed to fetch jobs feed: %s", exc)
        return {"status": "error", "detail": str(exc)}

    created = 0
    for item in items:
        _, was_created = Job.objects.update_or_create(
            external_id=item.get("external_id", ""),
            defaults={
                "title": item.get("title", ""),
                "company": item.get("company", ""),
                "description": item.get("description", ""),
                "type": item.get("type", Job.Type.FULL_TIME),
                "location": item.get("location", ""),
                "deadline": item.get("deadline") or None,
                "apply_url": item.get("apply_url", ""),
                "source": Job.Source.EXTERNAL,
            },
        )
        created += int(was_created)
    return {"status": "ok", "created": created, "total": len(items)}
