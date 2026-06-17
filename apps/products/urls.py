from rest_framework.routers import DefaultRouter

from apps.products.views import ProductImageViewSet, ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("product-images", ProductImageViewSet)

urlpatterns = router.urls
