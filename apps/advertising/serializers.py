from rest_framework import serializers

from apps.advertising.models import AdPlan, Advertisement


class AdPlanSerializer(serializers.ModelSerializer):
    placement_display = serializers.CharField(source="get_placement_display", read_only=True)

    class Meta:
        model = AdPlan
        fields = (
            "id",
            "name",
            "placement",
            "placement_display",
            "price",
            "currency",
            "duration_days",
            "is_active",
        )


class AdvertisementSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = Advertisement
        fields = (
            "id",
            "uuid",
            "advertiser",
            "business",
            "plan",
            "plan_name",
            "title",
            "image",
            "target_url",
            "status",
            "starts_at",
            "ends_at",
            "impressions",
            "clicks",
            "created_at",
        )
        read_only_fields = ("advertiser", "status", "starts_at", "ends_at", "impressions", "clicks")
