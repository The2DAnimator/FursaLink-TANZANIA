from rest_framework.routers import DefaultRouter

from apps.subscriptions.views import PaymentViewSet, PlanViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register("plans", PlanViewSet)
router.register("subscriptions", SubscriptionViewSet, basename="subscription")
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = router.urls
