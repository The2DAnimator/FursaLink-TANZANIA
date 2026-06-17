from django.db import models

from apps.core.models import Region, TimeStampedModel


class MarketCategory(models.TextChoices):
    CROPS = "crops", "Crops"
    LIVESTOCK = "livestock", "Livestock"
    BUILDING_MATERIALS = "building_materials", "Building Materials"
    FUEL = "fuel", "Fuel"
    ELECTRONICS = "electronics", "Electronics"


class Market(models.Model):
    """A physical market / trading point where prices are recorded."""

    name = models.CharField(max_length=160, db_index=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ("name",)
        unique_together = ("name", "region")

    def __str__(self):
        return self.name


class MarketPrice(TimeStampedModel):
    """A price observation for a commodity at a market on a given date."""

    product = models.CharField(max_length=160, db_index=True)
    category = models.CharField(max_length=20, choices=MarketCategory.choices, db_index=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="prices")
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="TZS")
    unit = models.CharField(max_length=30, default="kg")
    date = models.DateField(db_index=True)

    class Meta:
        ordering = ("-date",)
        indexes = [
            models.Index(fields=["product", "date"]),
            models.Index(fields=["category", "region", "date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "market", "unit", "date"], name="unique_price_observation"
            )
        ]

    def __str__(self):
        return f"{self.product} @ {self.market} = {self.price} {self.currency}/{self.unit}"
