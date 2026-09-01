from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from accounts.tests.utils import create_user
from offers.tests import create_offer
from reviews.models import Review


class BaseInfoTests(APITestCase):
    url = reverse_lazy("base-info")

    def test_is_public(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {
                "review_count",
                "average_rating",
                "business_profile_count",
                "offer_count",
            },
        )

    def test_returns_zero_values_on_empty_database(self):
        response = self.client.get(self.url)

        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["business_profile_count"], 0)
        self.assertEqual(response.data["offer_count"], 0)

    def test_aggregates_platform_statistics(self):
        business = create_user("biz", User.RoleChoices.BUSINESS)
        other_business = create_user("biz2", User.RoleChoices.BUSINESS)
        customer = create_user("cust", User.RoleChoices.CUSTOMER)

        create_offer(business)
        create_offer(other_business, title="Logo Paket")

        Review.objects.create(
            business_user=business, reviewer=customer, rating=4, description="Gut"
        )
        Review.objects.create(
            business_user=other_business,
            reviewer=customer,
            rating=5,
            description="Sehr gut",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.data["review_count"], 2)
        self.assertEqual(response.data["average_rating"], 4.5)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 2)
