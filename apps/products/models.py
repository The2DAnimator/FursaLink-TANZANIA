from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.businesses.models import Business
from apps.core.models import Category, Region, TimeStampedModel


class Product(TimeStampedModel):
    class Condition(models.TextChoices):
        NEW = "new", "New"
        USED = "used", "Used"
        REFURBISHED = "refurbished", "Refurbished"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products"
    )
    business = models.ForeignKey(
        Business, null=True, blank=True, on_delete=models.SET_NULL, related_name="products"
    )
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL, related_name="products"
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="TZS")
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=30, default="piece")
    condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.NEW)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["category", "region"]),
            models.Index(fields=["is_active", "price"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            slug = base
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.quantity > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ("-is_primary", "id")

    def __str__(self):
        return f"Image<{self.product.name}>"
