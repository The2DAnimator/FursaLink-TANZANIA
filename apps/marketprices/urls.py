from rest_framework.routers import DefaultRouter

from apps.marketprices.views import MarketPriceViewSet, MarketViewSet

router = DefaultRouter()
router.register("markets", MarketViewSet)
router.register("market-prices", MarketPriceViewSet)

urlpatterns = router.urls
