from django.db.models import Avg, Max, Min
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly
from apps.marketprices.models import Market, MarketPrice
from apps.marketprices.serializers import (
    MarketPriceSerializer,
    MarketSerializer,
    PriceTrendSerializer,
)


class MarketViewSet(viewsets.ModelViewSet):
    queryset = Market.objects.select_related("region")
    serializer_class = MarketSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("region",)
    search_fields = ("name",)


class MarketPriceViewSet(viewsets.ModelViewSet):
    queryset = MarketPrice.objects.select_related("market", "region")
    serializer_class = MarketPriceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("product", "category", "market", "region")
    search_fields = ("product",)
    ordering_fields = ("date", "price")

    @extend_schema(
        parameters=[
            OpenApiParameter("product", str, required=False),
            OpenApiParameter("category", str, required=False),
            OpenApiParameter("region", int, required=False),
        ],
        responses=PriceTrendSerializer(many=True),
    )
    @action(detail=False, methods=["get"])
    def trends(self, request):
        """Historical daily price trend (avg/min/max) for the filtered query."""
        qs = self.filter_queryset(self.get_queryset())
        data = (
            qs.values("date")
            .annotate(
                avg_price=Avg("price"), min_price=Min("price"), max_price=Max("price")
            )
            .order_by("date")
        )
        result = [
            {
                "date": row["date"],
                "avg_price": float(row["avg_price"]),
                "min_price": float(row["min_price"]),
                "max_price": float(row["max_price"]),
            }
            for row in data
        ]
        return Response(PriceTrendSerializer(result, many=True).data)

    @action(detail=False, methods=["get"], url_path="regional-comparison")
    def regional_comparison(self, request):
        """Average price per region for the filtered product/category."""
        qs = self.filter_queryset(self.get_queryset())
        data = (
            qs.values("region__name")
            .annotate(avg_price=Avg("price"))
            .order_by("-avg_price")
        )
        return Response(
            [{"region": r["region__name"], "avg_price": float(r["avg_price"])} for r in data]
        )
