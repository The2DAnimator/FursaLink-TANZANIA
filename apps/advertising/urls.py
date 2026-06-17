from rest_framework.routers import DefaultRouter

from apps.advertising.views import AdPlanViewSet, AdvertisementViewSet

router = DefaultRouter()
router.register("ad-plans", AdPlanViewSet)
router.register("advertisements", AdvertisementViewSet)

urlpatterns = router.urls
