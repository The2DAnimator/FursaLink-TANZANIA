"""Collect tenders from an external JSON feed.

Expects the feed (settings.EXTERNAL_FEEDS['TENDERS_FEED_URL']) to return a list
of objects with keys: organization, tender_number, title, description, sector,
closing_date, documents_url, external_id. Records are upserted by external_id.
"""
import logging

import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def collect_external_tenders():
    url = settings.EXTERNAL_FEEDS.get("TENDERS_FEED_URL")
    if not url:
        logger.info("TENDERS_FEED_URL not configured; skipping tender collection")
        return {"status": "skipped"}

    from apps.tenders.models import Tender

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        items = resp.json()
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("Failed to fetch tenders feed: %s", exc)
        return {"status": "error", "detail": str(exc)}

    created = 0
    for item in items:
        _, was_created = Tender.objects.update_or_create(
            external_id=item.get("external_id") or item.get("tender_number", ""),
            defaults={
                "organization": item.get("organization", ""),
                "tender_number": item.get("tender_number", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "sector": item.get("sector", Tender.Sector.GOVERNMENT),
                "closing_date": item.get("closing_date") or None,
                "documents_url": item.get("documents_url", ""),
                "source": Tender.Source.EXTERNAL,
            },
        )
        created += int(was_created)
    return {"status": "ok", "created": created, "total": len(items)}
