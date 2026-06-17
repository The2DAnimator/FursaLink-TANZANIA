from rest_framework.routers import DefaultRouter

from apps.leads.views import LeadViewSet

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")

urlpatterns = router.urls
