from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.leads.models import Lead
from apps.leads.serializers import LeadSerializer


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("business", "type", "status")
    ordering_fields = ("score", "created_at")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lead.objects.none()
        user = self.request.user
        qs = Lead.objects.select_related("business", "created_by")
        if user.is_super_admin or user.is_staff:
            return qs
        # Business owners see leads for their businesses; users see leads they made.
        return qs.filter(business__owner=user) | qs.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
