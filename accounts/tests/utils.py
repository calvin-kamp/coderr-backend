from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import Profile, User

PASSWORD = "SuperSecret123!"


def create_user(username, user_type, **extra):
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
    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def logout(self):
        self.client.credentials()
