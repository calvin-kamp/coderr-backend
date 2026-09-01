from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
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
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="unique_review_per_business_user",
            )
        ]

    def __str__(self):
        return f"{self.reviewer} -> {self.business_user} ({self.rating})"
