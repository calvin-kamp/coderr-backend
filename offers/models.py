from django.conf import settings
from django.db import models


class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="offers",
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offers/", blank=True, null=True)
    description = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    class OfferChoices(models.TextChoices):
        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    offer = models.ForeignKey(
        Offer,
        related_name="details",
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.IntegerField()
    features = models.JSONField(default=list)

    offer_type = models.CharField(
        max_length=8,
        choices=OfferChoices.choices,
        default=OfferChoices.BASIC,
    )

    class Meta:
        ordering = ["price"]
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer",
            )
        ]

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"
