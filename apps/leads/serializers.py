from rest_framework import serializers

from apps.leads.models import Lead


class LeadSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.name", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "uuid",
            "business",
            "business_name",
            "created_by",
            "type",
            "type_display",
            "contact_name",
            "message",
            "industry",
            "status",
            "score",
            "created_at",
        )
        read_only_fields = ("created_by", "score")
