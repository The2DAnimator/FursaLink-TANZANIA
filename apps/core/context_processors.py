from django.conf import settings


def site_settings(request):
    """Expose a few safe values to all templates."""
    return {
        "SITE_NAME": "FursaLink Tanzania",
        "GOOGLE_MAPS_API_KEY": settings.INTEGRATIONS.get("GOOGLE_MAPS_API_KEY", ""),
    }
