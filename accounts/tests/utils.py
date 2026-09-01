"""Shared helpers for the API test suite.

Every test module builds its users through ``create_user`` so a user always
comes with the profile that registration would have created for it, and
authenticates through ``BaseAPITestCase`` rather than assembling the token
header by hand.
"""

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import Profile, User

PASSWORD = "SuperSecret123!"


def create_user(username, user_type, **extra):
    """Create a user with its profile, mirroring what registration does."""
    user = User.objects.create_user(
        username=username,
        email=extra.pop("email", f"{username}@example.com"),
        password=extra.pop("password", PASSWORD),
        type=user_type,
        **extra,
    )
    Profile.objects.create(user=user)
    return user


class BaseAPITestCase(APITestCase):
    """Base class that adds token authentication to the API client."""

    def authenticate(self, user):
        """Send the token of ``user`` with every following request."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def logout(self):
        """Drop the token header again."""
        self.client.credentials()
