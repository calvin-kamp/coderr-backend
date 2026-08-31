from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        BUSINESS = "business"
        CUSTOMER = "customer"

    type = models.TextField(choices=RoleChoices, max_length=8)
    email = models.EmailField(unique=True, blank=False)

    REQUIRED_FIELDS = ["email", "type"]


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="user",
        on_delete=models.CASCADE,
    )

    first_name = models.CharField(blank=True, default="")
    last_name = models.CharField(blank=True, default="")
    location = models.CharField(blank=True, default="")
    tel = models.CharField(blank=True, default="")
    description = models.CharField(blank=True, default="")
    working_hours = models.CharField(blank=True, default="")

    type = models.TextField()
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=timezone.now)
