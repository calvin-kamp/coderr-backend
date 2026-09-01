"""Database models for offers.

An offer is a service a business user sells. It never carries a price itself:
the price, the delivery time and the feature list live on the three detail rows
(basic, standard, premium) that belong to it. Everything the API exposes as
``min_price`` or ``min_delivery_time`` is therefore aggregated from the details
at query time rather than stored on the offer.

Contents:
  * Offer       -- the offer itself, owned by a business user.
  * OfferDetail -- one package tier of an offer.
"""

from django.conf import settings
from django.db import models


class Offer(models.Model):
    """A service offered by a business user."""

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
        """Newest changes first, matching the default order of the list view."""

        ordering = ["-updated_at"]

    def __str__(self):
        """Return the offer title."""
        return self.title


class OfferDetail(models.Model):
    """One package tier of an offer.

    An offer has exactly three of these, one per ``offer_type``. The unique
    constraint enforces that on the database level and makes ``offer_type`` a
    stable identifier within an offer, which is what the update path in the
    serializer keys on. The serializer additionally rejects a payload that does
    not contain all three tiers on creation.
    """

    class OfferChoices(models.TextChoices):
        """The three package tiers every offer consists of."""

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
        """Cheapest tier first, with one tier of each type per offer."""

        ordering = ["price"]
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer",
            )
        ]

    def __str__(self):
        """Return the offer title together with this tier."""
        return f"{self.offer.title} - {self.offer_type}"
