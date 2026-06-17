from django.db.models import F
from rest_framework import decorators, viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.advertising.models import AdPlan, Advertisement
from apps.advertising.serializers import AdPlanSerializer, AdvertisementSerializer
from apps.core.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class AdPlanViewSet(viewsets.ModelViewSet):
    queryset = AdPlan.objects.all()
    serializer_class = AdPlanSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("placement", "is_active")


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.select_related("advertiser", "business", "plan")
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ("status", "plan", "business")

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def click(self, request, pk=None):
        Advertisement.objects.filter(pk=pk).update(clicks=F("clicks") + 1)
        return Response({"status": "ok"})

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def impression(self, request, pk=None):
        Advertisement.objects.filter(pk=pk).update(impressions=F("impressions") + 1)
        return Response({"status": "ok"})
