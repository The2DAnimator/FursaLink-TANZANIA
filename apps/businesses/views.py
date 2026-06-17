from django.db.models import F
from rest_framework import decorators, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.businesses.models import Business, Review
from apps.businesses.serializers import BusinessSerializer, ReviewSerializer
from apps.core.permissions import IsAdmin, IsOwnerOrReadOnly


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.select_related("owner", "category", "region", "district")
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ("category", "region", "district", "verification_status", "is_featured")
    search_fields = ("name", "description", "address")
    ordering_fields = ("created_at", "views_count", "name")
    lookup_field = "slug"

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.action(detail=True, methods=["get"])
    def view(self, request, slug=None):
        """Register a view and return the business (used by the detail page)."""
        Business.objects.filter(slug=slug).update(views_count=F("views_count") + 1)
        return Response(self.get_serializer(self.get_object()).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def verify(self, request, slug=None):
        business = self.get_object()
        business.verification_status = Business.VerificationStatus.VERIFIED
        business.save(update_fields=["verification_status"])
        return Response(self.get_serializer(business).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def feature(self, request, slug=None):
        business = self.get_object()
        business.is_featured = True
        business.save(update_fields=["is_featured"])
        return Response(self.get_serializer(business).data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "business")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ("business", "rating")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
