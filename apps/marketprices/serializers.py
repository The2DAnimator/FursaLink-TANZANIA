from rest_framework import serializers

from apps.marketprices.models import Market, MarketPrice


class MarketSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = Market
        fields = ("id", "name", "region", "region_name")


class MarketPriceSerializer(serializers.ModelSerializer):
    market_name = serializers.CharField(source="market.name", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = MarketPrice
        fields = (
            "id",
            "uuid",
            "product",
            "category",
            "category_display",
            "market",
            "market_name",
            "region",
            "price",
            "currency",
            "unit",
            "date",
            "created_at",
        )


class PriceTrendSerializer(serializers.Serializer):
    """Aggregated trend point used by the price-intelligence charts."""

    date = serializers.DateField()
    avg_price = serializers.FloatField()
    min_price = serializers.FloatField()
    max_price = serializers.FloatField()
