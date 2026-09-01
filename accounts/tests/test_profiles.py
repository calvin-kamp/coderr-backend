from django.urls import reverse
from rest_framework import status

from accounts.models import User

from .utils import BaseAPITestCase, create_user


class ProfileDetailTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.url = reverse("profile-detail", args=[self.business.id])

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_empty_strings_instead_of_null(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in (
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ):
            self.assertEqual(response.data[field], "", msg=field)

        self.assertEqual(response.data["user"], self.business.id)
        self.assertEqual(response.data["type"], "business")

    def test_returns_404_for_unknown_user(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("profile-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_patch(self):
        self.authenticate(self.business)
        response = self.client.patch(
            self.url,
            {
                "first_name": "Max",
                "last_name": "Mustermann",
                "location": "Berlin",
                "tel": "987654321",
                "description": "Updated",
                "working_hours": "10-18",
                "email": "new_email@business.de",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["email"], "new_email@business.de")

        self.business.refresh_from_db()
        self.assertEqual(self.business.first_name, "Max")
        self.assertEqual(self.business.email, "new_email@business.de")

    def test_other_user_cannot_patch(self):
        self.authenticate(self.customer)
        response = self.client.patch(self.url, {"location": "Hagen"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_email_already_in_use(self):
        self.authenticate(self.business)
        response = self.client.patch(
            self.url, {"email": self.customer.email}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class ProfileListTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)

    def test_business_list_requires_authentication(self):
        response = self.client.get(reverse("business-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_list_returns_only_business_users(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("business-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], self.business.id)
        self.assertEqual(response.data[0]["type"], "business")
        self.assertIn("working_hours", response.data[0])

    def test_customer_list_returns_only_customers(self):
        self.authenticate(self.business)
        response = self.client.get(reverse("customer-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], self.customer.id)
        self.assertEqual(response.data[0]["type"], "customer")
        self.assertNotIn("location", response.data[0])
