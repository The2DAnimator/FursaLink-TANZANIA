from rest_framework import serializers

from apps.businesses.models import Business, Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "business", "user", "user_name", "rating", "comment", "created_at")
        read_only_fields = ("user",)


class BusinessSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = Business
        fields = (
            "id",
            "uuid",
            "owner",
            "owner_name",
            "name",
            "slug",
            "category",
            "category_name",
            "description",
            "logo",
            "cover_image",
            "address",
            "region",
            "region_name",
            "district",
            "latitude",
            "longitude",
            "phone",
            "email",
            "website",
            "facebook",
            "instagram",
            "twitter",
            "linkedin",
            "verification_status",
            "is_featured",
            "featured_until",
            "views_count",
            "average_rating",
            "reviews_count",
            "created_at",
        )
        read_only_fields = (
            "owner",
            "slug",
            "verification_status",
            "is_featured",
            "featured_until",
            "views_count",
        )
