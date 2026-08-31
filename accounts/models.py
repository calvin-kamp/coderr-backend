from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        BUSINESS = "business", "Business"
        CUSTOMER = "customer", "Customer"

    type = models.CharField(max_length=8, choices=RoleChoices.choices)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email", "type"]

    @property
    def is_business(self):
        return self.type == self.RoleChoices.BUSINESS

    @property
    def is_customer(self):
        return self.type == self.RoleChoices.CUSTOMER


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )

    file = models.FileField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=50, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user_id"]

    def __str__(self):
        return f"{self.user.username} ({self.user.type})"
