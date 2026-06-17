from rest_framework.routers import DefaultRouter

from apps.core.views import CategoryViewSet, DistrictViewSet, RegionViewSet

router = DefaultRouter()
router.register("regions", RegionViewSet)
router.register("districts", DistrictViewSet)
router.register("categories", CategoryViewSet)

urlpatterns = router.urls
