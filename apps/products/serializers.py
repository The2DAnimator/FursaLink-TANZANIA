from rest_framework import serializers

from apps.products.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "product", "image", "is_primary")


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source="seller.full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "uuid",
            "seller",
            "seller_name",
            "business",
            "name",
            "slug",
            "category",
            "category_name",
            "description",
            "price",
            "currency",
            "quantity",
            "unit",
            "condition",
            "region",
            "location",
            "is_active",
            "in_stock",
            "views_count",
            "images",
            "created_at",
        )
        read_only_fields = ("seller", "slug", "views_count")
