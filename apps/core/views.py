from rest_framework import viewsets

from apps.core.models import Category, District, Region
from apps.core.permissions import IsAdminOrReadOnly
from apps.core.serializers import (
    CategorySerializer,
    DistrictSerializer,
    RegionSerializer,
)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name",)


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.select_related("region").all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("region",)
    search_fields = ("name",)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("kind", "parent")
    search_fields = ("name", "slug")
