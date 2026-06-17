from rest_framework import serializers

from apps.opportunities.models import Opportunity


class OpportunitySerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source="posted_by.full_name", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Opportunity
        fields = (
            "id",
            "uuid",
            "posted_by",
            "posted_by_name",
            "business",
            "type",
            "type_display",
            "title",
            "description",
            "industry",
            "region",
            "location",
            "budget_min",
            "budget_max",
            "currency",
            "deadline",
            "status",
            "views_count",
            "created_at",
        )
        read_only_fields = ("posted_by", "status", "views_count")
