"""Versioned REST API URL configuration (mounted under /api/v1/)."""

from django.urls import include, path

urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.businesses.urls")),
    path("", include("apps.products.urls")),
    path("", include("apps.opportunities.urls")),
    path("", include("apps.tenders.urls")),
    path("", include("apps.jobs.urls")),
    path("", include("apps.marketprices.urls")),
    path("", include("apps.matching.urls")),
    path("", include("apps.leads.urls")),
    path("", include("apps.advertising.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.analytics.urls")),
    path("", include("apps.subscriptions.urls")),
]
