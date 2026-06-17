from rest_framework.routers import DefaultRouter

from apps.tenders.views import TenderViewSet

router = DefaultRouter()
router.register("tenders", TenderViewSet)

urlpatterns = router.urls
