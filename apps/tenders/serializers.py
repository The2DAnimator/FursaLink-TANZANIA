from rest_framework import serializers

from apps.tenders.models import Tender


class TenderSerializer(serializers.ModelSerializer):
    sector_display = serializers.CharField(source="get_sector_display", read_only=True)

    class Meta:
        model = Tender
        fields = (
            "id",
            "uuid",
            "organization",
            "tender_number",
            "title",
            "description",
            "sector",
            "sector_display",
            "region",
            "closing_date",
            "documents_url",
            "document",
            "source",
            "external_id",
            "is_active",
            "created_at",
        )
