from rest_framework.routers import DefaultRouter

from apps.businesses.views import BusinessViewSet, ReviewViewSet

router = DefaultRouter()
router.register("businesses", BusinessViewSet)
router.register("reviews", ReviewViewSet)

urlpatterns = router.urls
