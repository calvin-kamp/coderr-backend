"""Database model for orders.

An order is a snapshot, not a reference. When a customer books a package tier,
its title, price, revisions, delivery time and features are copied onto the
order. That way a later edit or deletion of the offer does not change what was
agreed on, which is also why there is no foreign key to ``OfferDetail``.

Contents:
  * Order -- one booked package tier, linking a customer to a business user.
"""

from django.conf import settings
from django.db import models

from offers.models import OfferDetail


class Order(models.Model):
    """A package tier booked by a customer from a business user.

    Both parties are foreign keys to the same user model, so each one needs its
    own ``related_name``: ``user.orders`` are the orders placed,
    ``user.received_orders`` the ones sold.

    ``offer_type`` reuses the choices of ``OfferDetail`` so the two models
    cannot drift apart.
    """

    class StatusChoices(models.TextChoices):
        """The states an order moves through."""

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
        """Newest orders first."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return the booked title together with the current status."""
        return f"{self.title} ({self.status})"
