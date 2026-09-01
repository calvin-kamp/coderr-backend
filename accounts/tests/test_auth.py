from django.urls import reverse_lazy
from rest_framework import status

from accounts.models import Profile, User

from .utils import PASSWORD, BaseAPITestCase, create_user


class RegistrationTests(BaseAPITestCase):
    url = reverse_lazy("register")

    def test_creates_user_profile_and_token(self):
        response = self.client.post(
            self.url,
            {
                "username": "new_customer",
                "email": "new_customer@example.com",
                "password": PASSWORD,
                "repeated_password": PASSWORD,
                "type": "customer",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data),
            {"token", "username", "email", "user_id"},
        )
        user = User.objects.get(username="new_customer")
        self.assertEqual(response.data["user_id"], user.id)
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_rejects_mismatched_passwords(self):
        response = self.client.post(
            self.url,
            {
                "username": "mismatch",
                "email": "mismatch@example.com",
                "password": PASSWORD,
                "repeated_password": "SomethingElse123!",
                "type": "customer",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)

    def test_rejects_duplicate_username_and_email(self):
        create_user("taken", User.RoleChoices.CUSTOMER, email="taken@example.com")

        response = self.client.post(
            self.url,
            {
                "username": "taken",
                "email": "taken@example.com",
                "password": PASSWORD,
                "repeated_password": PASSWORD,
                "type": "customer",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)

    def test_rejects_missing_type(self):
        response = self.client.post(
            self.url,
            {
                "username": "no_type",
                "email": "no_type@example.com",
                "password": PASSWORD,
                "repeated_password": PASSWORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)


class LoginTests(BaseAPITestCase):
    url = reverse_lazy("login")

    def setUp(self):
        self.user = create_user("login_user", User.RoleChoices.CUSTOMER)

    def test_returns_token(self):
        response = self.client.post(
            self.url,
            {"username": "login_user", "password": PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertTrue(response.data["token"])

    def test_rejects_wrong_password(self):
        response = self.client.post(
            self.url,
            {"username": "login_user", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
