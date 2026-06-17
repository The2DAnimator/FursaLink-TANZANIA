from django.urls import path

from apps.analytics.views import (
    OverviewAnalyticsView,
    RevenueTrendView,
    UserGrowthView,
)

urlpatterns = [
    path("analytics/overview/", OverviewAnalyticsView.as_view(), name="analytics-overview"),
    path("analytics/user-growth/", UserGrowthView.as_view(), name="analytics-user-growth"),
    path("analytics/revenue-trend/", RevenueTrendView.as_view(), name="analytics-revenue-trend"),
]
