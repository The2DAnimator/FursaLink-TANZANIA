"""Analytics dashboard endpoints (consumed by Chart.js on the frontend)."""
from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.businesses.models import Business
from apps.jobs.models import JobApplication
from apps.leads.models import Lead
from apps.products.models import Product
from apps.subscriptions.models import Payment


class OverviewAnalyticsView(APIView):
    """Platform-wide metrics for a business owner or admin dashboard."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        user = request.user
        is_admin = user.is_super_admin or user.is_staff

        businesses = Business.objects.all() if is_admin else Business.objects.filter(owner=user)
        products = Product.objects.all() if is_admin else Product.objects.filter(seller=user)
        leads = Lead.objects.all() if is_admin else Lead.objects.filter(business__owner=user)
        applications = (
            JobApplication.objects.all()
            if is_admin
            else JobApplication.objects.filter(job__posted_by=user)
        )
        payments = Payment.objects.filter(status=Payment.Status.SUCCESS)
        if not is_admin:
            payments = payments.filter(user=user)

        data = {
            "business_views": businesses.aggregate(v=Sum("views_count"))["v"] or 0,
            "product_views": products.aggregate(v=Sum("views_count"))["v"] or 0,
            "businesses": businesses.count(),
            "products": products.count(),
            "leads_generated": leads.count(),
            "applications": applications.count(),
            "revenue": float(payments.aggregate(v=Sum("amount"))["v"] or 0),
        }
        return Response(data)


class UserGrowthView(APIView):
    """Monthly new-user counts for the last 12 months (admin only metric)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        from apps.accounts.models import User

        since = timezone.now() - timedelta(days=365)
        rows = (
            User.objects.filter(date_joined__gte=since)
            .annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        return Response(
            [{"month": r["month"].strftime("%Y-%m"), "count": r["count"]} for r in rows]
        )


class RevenueTrendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        qs = Payment.objects.filter(status=Payment.Status.SUCCESS)
        user = request.user
        if not (user.is_super_admin or user.is_staff):
            qs = qs.filter(user=user)
        rows = (
            qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        return Response(
            [{"month": r["month"].strftime("%Y-%m"), "total": float(r["total"])} for r in rows]
        )
