from django.db.models import F
from django_filters import rest_framework as df
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.permissions import IsOwnerOrReadOnly
from apps.products.models import Product, ProductImage
from apps.products.serializers import ProductImageSerializer, ProductSerializer


class ProductFilter(df.FilterSet):
    min_price = df.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = df.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ("category", "region", "condition", "is_active", "business")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("seller", "category", "region").prefetch_related(
        "images"
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ("name", "description", "location")
    ordering_fields = ("price", "created_at", "views_count")
    lookup_field = "slug"

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        Product.objects.filter(slug=kwargs.get("slug")).update(views_count=F("views_count") + 1)
        return super().retrieve(request, *args, **kwargs)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.select_related("product")
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ("product",)
