from rest_framework.routers import DefaultRouter

from apps.jobs.views import JobApplicationViewSet, JobViewSet

router = DefaultRouter()
router.register("jobs", JobViewSet)
router.register("job-applications", JobApplicationViewSet, basename="job-application")

urlpatterns = router.urls
