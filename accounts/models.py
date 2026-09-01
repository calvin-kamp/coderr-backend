"""Database models for user accounts.

The project ships a custom user model because the whole API is built around the
distinction between business and customer accounts. That role lives on the user
itself rather than in a side table, so every other app can read it through
``User.type`` or the ``is_business`` / ``is_customer`` helpers without an extra
query.

Contents:
  * User    -- ``AbstractUser`` plus a required ``type`` and a unique ``email``.
  * Profile -- one-to-one extension holding the optional public profile fields.
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Platform user, either a business or a customer account.

    ``email`` is overridden to be unique because the API treats it as a second
    identifier next to the username, and profile updates have to reject an
    address that is already taken.

    ``REQUIRED_FIELDS`` only affects the ``createsuperuser`` command; the API
    sets both fields explicitly when registering a user.
    """

    class RoleChoices(models.TextChoices):
        """The two roles a user can have on the platform."""

        BUSINESS = "business", "Business"
        CUSTOMER = "customer", "Customer"

    type = models.CharField(max_length=8, choices=RoleChoices.choices)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email", "type"]

    @property
    def is_business(self):
        """Return whether this user may create offers and receive orders."""
        return self.type == self.RoleChoices.BUSINESS

    @property
    def is_customer(self):
        """Return whether this user may place orders and write reviews."""
        return self.type == self.RoleChoices.CUSTOMER


class Profile(models.Model):
    """Public profile data belonging to exactly one user.

    A profile is created together with the user during registration, so every
    user is guaranteed to have one and the API never has to handle a missing
    profile.

    The text fields default to an empty string instead of allowing NULL, because
    the API answers with ``""`` rather than ``null`` for ``location``, ``tel``,
    ``description`` and ``working_hours``.
    """

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
        """Order profiles by their user so list responses stay stable."""

        ordering = ["user_id"]

    def __str__(self):
        """Return the username together with its role."""
        return f"{self.user.username} ({self.user.type})"
