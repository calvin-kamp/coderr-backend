"""Tests for the review endpoints.

Covers the list with its filters and ordering, creation including the one
review per business user rule, and the author-only rules for update and delete.
"""

from django.urls import reverse, reverse_lazy
from rest_framework import status

from accounts.models import User
from accounts.tests.utils import BaseAPITestCase, create_user
from reviews.models import Review


class ReviewListTests(BaseAPITestCase):
    """GET /api/reviews/ including filters and ordering."""

    url = reverse_lazy("review-list")

    def setUp(self):
        """Create the users and reviews the test methods work on."""
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.other_business = create_user("biz2", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.other_customer = create_user("cust2", User.RoleChoices.CUSTOMER)

        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Sehr professioneller Service.",
        )
        self.other_review = Review.objects.create(
            business_user=self.other_business,
            reviewer=self.other_customer,
            rating=5,
            description="Top Qualität!",
        )

    def test_requires_authentication(self):
        """Requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_unpaginated_list(self):
        """Returns unpaginated list."""
        self.authenticate(self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            set(response.data[0]),
            {
                "id",
                "business_user",
                "reviewer",
                "rating",
                "description",
                "created_at",
                "updated_at",
            },
        )

    def test_filters_by_business_user_id(self):
        """Filters by business user id."""
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"business_user_id": self.business.id})

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.review.id)

    def test_filters_by_reviewer_id(self):
        """Filters by reviewer id."""
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"reviewer_id": self.other_customer.id})

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.other_review.id)

    def test_orders_by_rating(self):
        """Ordering by rating sorts ascending."""
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"ordering": "rating"})

        ratings = [item["rating"] for item in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_orders_by_updated_at(self):
        """Ordering by updated_at sorts ascending."""
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"ordering": "updated_at"})

        timestamps = [item["updated_at"] for item in response.data]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_business_user_may_read(self):
        """Business user may read."""
        self.authenticate(self.business)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReviewCreateTests(BaseAPITestCase):
    """POST /api/reviews/."""

    url = reverse_lazy("review-list")

    def setUp(self):
        """Create the users and reviews the test methods work on."""
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.payload = {
            "business_user": self.business.id,
            "rating": 4,
            "description": "Alles war toll!",
        }

    def test_requires_authentication(self):
        """Requires authentication."""
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_create_review(self):
        """Customer can create review."""
        self.authenticate(self.customer)
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["reviewer"], self.customer.id)
        self.assertEqual(response.data["rating"], 4)

    def test_business_user_is_forbidden(self):
        """Business user is forbidden."""
        self.authenticate(self.business)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_second_review_for_same_business_returns_400(self):
        """Second review for same business returns 400."""
        self.authenticate(self.customer)
        self.client.post(self.url, self.payload, format="json")
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviewer_cannot_be_spoofed(self):
        """Reviewer cannot be spoofed."""
        self.authenticate(self.customer)
        other = create_user("cust2", User.RoleChoices.CUSTOMER)
        response = self.client.post(
            self.url, {**self.payload, "reviewer": other.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reviewer"], self.customer.id)

    def test_rejects_review_for_customer_user(self):
        """Rejects review for customer user."""
        self.authenticate(self.customer)
        other = create_user("cust2", User.RoleChoices.CUSTOMER)
        response = self.client.post(
            self.url, {**self.payload, "business_user": other.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("business_user", response.data)

    def test_rejects_rating_out_of_range(self):
        """Rejects rating out of range."""
        self.authenticate(self.customer)
        response = self.client.post(
            self.url, {**self.payload, "rating": 6}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)


class ReviewUpdateDeleteTests(BaseAPITestCase):
    """PATCH and DELETE /api/reviews/<id>/."""

    def setUp(self):
        """Create the users and reviews the test methods work on."""
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.other_customer = create_user("cust2", User.RoleChoices.CUSTOMER)
        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Sehr professioneller Service.",
        )
        self.url = reverse("review-detail", args=[self.review.id])

    def test_reviewer_can_patch(self):
        """Reviewer can patch."""
        self.authenticate(self.customer)
        response = self.client.patch(
            self.url,
            {"rating": 5, "description": "Noch besser als erwartet!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["reviewer"], self.customer.id)

    def test_other_user_cannot_patch(self):
        """Other user cannot patch."""
        self.authenticate(self.other_customer)
        response = self.client.patch(self.url, {"rating": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_editable_field_returns_400(self):
        """Non editable field returns 400."""
        self.authenticate(self.customer)
        response = self.client.patch(
            self.url, {"business_user": self.business.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("business_user", response.data)

    def test_unknown_review_returns_404(self):
        """Unknown review returns 404."""
        self.authenticate(self.customer)
        response = self.client.patch(
            reverse("review-detail", args=[9999]), {"rating": 5}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reviewer_can_delete(self):
        """Reviewer can delete."""
        self.authenticate(self.customer)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())

    def test_other_user_cannot_delete(self):
        """Other user cannot delete."""
        self.authenticate(self.other_customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
