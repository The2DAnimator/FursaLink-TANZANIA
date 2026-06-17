from rest_framework import serializers

from apps.subscriptions.models import Payment, Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "name",
            "tier",
            "price",
            "currency",
            "billing_period_days",
            "max_listings",
            "has_analytics",
            "has_lead_generation",
            "featured_placement",
            "priority_support",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "uuid",
            "user",
            "plan",
            "plan_name",
            "status",
            "started_at",
            "expires_at",
            "auto_renew",
            "is_active",
            "created_at",
        )
        read_only_fields = ("user", "status", "started_at", "expires_at")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "uuid",
            "user",
            "subscription",
            "amount",
            "currency",
            "provider",
            "purpose",
            "status",
            "reference",
            "provider_ref",
            "created_at",
        )
        read_only_fields = ("user", "status", "reference", "provider_ref")


class CheckoutSerializer(serializers.Serializer):
    """Subscribe to a plan and pay via a chosen provider."""

    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())
    provider = serializers.ChoiceField(choices=Payment.Provider.choices)
    phone = serializers.CharField(required=False, allow_blank=True)
    token = serializers.CharField(required=False, allow_blank=True)
