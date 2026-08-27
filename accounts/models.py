from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        BUSINESS = "business"
        CUSTOMER = "customer"

    type = models.TextField(choices=RoleChoices, max_length=8)
    email = models.EmailField(unique=True, blank=False)

    REQUIRED_FIELDS = ["email", "type"]
