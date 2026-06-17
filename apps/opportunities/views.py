from rest_framework import decorators, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsOwnerOrReadOnly
from apps.opportunities.models import Opportunity
from apps.opportunities.serializers import OpportunitySerializer


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.select_related("posted_by", "business", "region")
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ("type", "status", "industry", "region", "business")
    search_fields = ("title", "description", "industry", "location")
    ordering_fields = ("created_at", "deadline", "budget_max")

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        opp = self.get_object()
        opp.status = Opportunity.Status.OPEN
        opp.save(update_fields=["status"])
        return Response(self.get_serializer(opp).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        opp = self.get_object()
        opp.status = Opportunity.Status.REJECTED
        opp.save(update_fields=["status"])
        return Response(self.get_serializer(opp).data)
