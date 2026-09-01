"""Database model for reviews.

A review is written by a customer about a business user. The pair of the two is
unique, so a customer can rate the same business only once. That rule is
enforced by a database constraint rather than only in the serializer.

Contents:
  * Review -- rating and text, linking a reviewer to a business user.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """A customer's rating of a business user.

    Both parties are foreign keys to the same user model, so each one needs its
    own ``related_name``: ``user.reviews`` are the ones received,
    ``user.reviewed`` the ones written.
    """

    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        on_delete=models.CASCADE,
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviewed",
        on_delete=models.CASCADE,
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Newest reviews first, one review per customer and business user.

        The serializer reports a repeat as a 400 through its
        ``UniqueTogetherValidator``; the constraint is the backstop for writes
        that bypass the API.
        """

        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="unique_review_per_business_user",
            )
        ]

    def __str__(self):
        """Return both parties together with the rating."""
        return f"{self.reviewer} -> {self.business_user} ({self.rating})"
