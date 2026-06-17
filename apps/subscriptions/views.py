from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly
from apps.integrations.payments import get_gateway
from apps.subscriptions.models import Payment, Plan, Subscription
from apps.subscriptions.serializers import (
    CheckoutSerializer,
    PaymentSerializer,
    PlanSerializer,
    SubscriptionSerializer,
)


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminOrReadOnly]


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Subscription.objects.none()
        user = self.request.user
        qs = Subscription.objects.select_related("plan", "user")
        if user.is_super_admin or user.is_staff:
            return qs
        return qs.filter(user=user)

    @extend_schema(request=CheckoutSerializer, responses=SubscriptionSerializer)
    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Subscribe to a plan and charge via the selected payment provider."""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data["plan"]
        provider = serializer.validated_data["provider"]

        gateway = get_gateway(provider)
        charge = gateway.charge(
            amount=plan.price,
            phone=serializer.validated_data.get("phone"),
            token=serializer.validated_data.get("token"),
            metadata={"plan": plan.tier, "user_id": request.user.id},
        )

        now = timezone.now()
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status=Subscription.Status.ACTIVE if charge.get("success") else Subscription.Status.EXPIRED,
            started_at=now,
            expires_at=now + timedelta(days=plan.billing_period_days),
        )
        Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=plan.price,
            currency=plan.currency,
            provider=provider,
            purpose=Payment.Purpose.SUBSCRIPTION,
            status=Payment.Status.SUCCESS if charge.get("success") else Payment.Status.FAILED,
            reference=charge["reference"],
            provider_ref=charge.get("provider_ref", ""),
            metadata=charge,
        )
        if not charge.get("success"):
            return Response(
                {"detail": "Payment failed", "charge": charge},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("status", "provider", "purpose")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()
        user = self.request.user
        qs = Payment.objects.select_related("user", "subscription")
        if user.is_super_admin or user.is_staff:
            return qs
        return qs.filter(user=user)
