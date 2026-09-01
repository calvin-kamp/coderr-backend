from django.conf import settings
from django.db import models

from offers.models import OfferDetail


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_orders",
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.IntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=8,
        choices=OfferDetail.OfferChoices.choices,
    )
    status = models.CharField(
        max_length=11,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"
