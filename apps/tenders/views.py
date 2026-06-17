from rest_framework import viewsets

from apps.core.permissions import IsAdminOrReadOnly
from apps.tenders.models import Tender
from apps.tenders.serializers import TenderSerializer


class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.select_related("region")
    serializer_class = TenderSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("sector", "region", "is_active", "source")
    search_fields = ("title", "organization", "tender_number", "description")
    ordering_fields = ("closing_date", "created_at")
