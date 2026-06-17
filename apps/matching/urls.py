from django.urls import path

from apps.matching.views import (
    MatchSellersView,
    RecommendOpportunitiesView,
    RecommendProductsView,
    SpamCheckView,
)

urlpatterns = [
    path("match/products/", RecommendProductsView.as_view(), name="match-products"),
    path("match/opportunities/", RecommendOpportunitiesView.as_view(), name="match-opportunities"),
    path("match/sellers/", MatchSellersView.as_view(), name="match-sellers"),
    path("match/spam-check/", SpamCheckView.as_view(), name="match-spam-check"),
]
