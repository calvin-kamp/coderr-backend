from django.urls import reverse, reverse_lazy
from rest_framework import status

from accounts.models import User
from accounts.tests.utils import BaseAPITestCase, create_user
from offers.models import Offer, OfferDetail


def detail_payload(offer_type, price, delivery_time, revisions=1):
    return {
        "title": f"{offer_type.capitalize()} Design",
        "revisions": revisions,
        "delivery_time_in_days": delivery_time,
        "price": price,
        "features": ["Logo Design", "Visitenkarte"],
        "offer_type": offer_type,
    }


def create_offer(
    user, title="Grafikdesign-Paket", prices=(100, 200, 500), days=(5, 7, 10)
):
    offer = Offer.objects.create(user=user, title=title, description="Beschreibung")
    for offer_type, price, day in zip(("basic", "standard", "premium"), prices, days):
        OfferDetail.objects.create(
            offer=offer,
            title=f"{offer_type} package",
            revisions=1,
            delivery_time_in_days=day,
            price=price,
            features=["A"],
            offer_type=offer_type,
        )
    return offer


class OfferListTests(BaseAPITestCase):
    url = reverse_lazy("offer-list")

    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.other_business = create_user("biz2", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.offer = create_offer(self.business, "Website Design")
        self.other_offer = create_offer(
            self.other_business, "Logo Paket", prices=(50, 60, 70), days=(2, 3, 4)
        )

    def test_returns_paginated_list_with_annotations(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"count", "next", "previous", "results"})
        self.assertEqual(response.data["count"], 2)

        result = next(
            item for item in response.data["results"] if item["id"] == self.offer.id
        )
        self.assertEqual(result["min_price"], 100)
        self.assertEqual(result["min_delivery_time"], 5)
        self.assertEqual(len(result["details"]), 3)
        self.assertEqual(set(result["details"][0]), {"id", "url"})
        self.assertEqual(
            set(result["user_details"]), {"first_name", "last_name", "username"}
        )

    def test_filters_by_creator_id(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"creator_id": self.business.id})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.offer.id)

    def test_filters_by_min_price(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"min_price": 100})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.offer.id)

    def test_filters_by_max_delivery_time(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"max_delivery_time": 4})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.other_offer.id)

    def test_search_matches_title(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"search": "Logo"})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.other_offer.id)

    def test_ordering_by_min_price(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"ordering": "min_price"})

        prices = [item["min_price"] for item in response.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_page_size_query_param(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url, {"page_size": 1})

        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["next"])


class OfferCreateTests(BaseAPITestCase):
    url = reverse_lazy("offer-list")

    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.payload = {
            "title": "Grafikdesign-Paket",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket.",
            "details": [
                detail_payload("basic", 100, 5, 2),
                detail_payload("standard", 200, 7, 5),
                detail_payload("premium", 500, 10, 10),
            ],
        }

    def test_requires_authentication(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_user_can_create(self):
        self.authenticate(self.business)
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(
            set(response.data["details"][0]),
            {
                "id",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
            },
        )
        self.assertEqual(Offer.objects.get(pk=response.data["id"]).user, self.business)

    def test_customer_user_is_forbidden(self):
        self.authenticate(self.customer)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_incomplete_details(self):
        self.authenticate(self.business)
        payload = {**self.payload, "details": self.payload["details"][:2]}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("details", response.data)

    def test_rejects_duplicate_offer_types(self):
        self.authenticate(self.business)
        payload = {
            **self.payload,
            "details": [
                detail_payload("basic", 100, 5),
                detail_payload("basic", 200, 7),
                detail_payload("premium", 500, 10),
            ],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferDetailEndpointTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.other_business = create_user("biz2", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.offer = create_offer(self.business)
        self.url = reverse("offer-detail", args=[self.offer.id])

    def test_retrieve_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_returns_detail_links(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.business.id)
        self.assertEqual(response.data["min_price"], 100)
        self.assertEqual(response.data["min_delivery_time"], 5)
        self.assertNotIn("user_details", response.data)
        self.assertTrue(
            response.data["details"][0]["url"].endswith(
                reverse(
                    "offerdetail-detail",
                    args=[response.data["details"][0]["id"]],
                )
            )
        )

    def test_retrieve_unknown_offer_returns_404(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("offer-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_patch_single_detail(self):
        self.authenticate(self.business)
        basic = self.offer.details.get(offer_type="basic")

        response = self.client.patch(
            self.url,
            {
                "title": "Updated Grafikdesign-Paket",
                "details": [detail_payload("basic", 120, 6, 3)],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Grafikdesign-Paket")
        self.assertEqual(len(response.data["details"]), 3)

        basic.refresh_from_db()
        self.assertEqual(basic.price, 120)
        self.assertEqual(basic.delivery_time_in_days, 6)
        self.assertEqual(self.offer.details.count(), 3)

    def test_other_business_user_cannot_patch(self):
        self.authenticate(self.other_business)
        response = self.client.patch(self.url, {"title": "Hijacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_patch(self):
        self.authenticate(self.customer)
        response = self.client.patch(self.url, {"title": "Hijacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete(self):
        self.authenticate(self.business)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=self.offer.id).exists())

    def test_other_business_user_cannot_delete(self):
        self.authenticate(self.other_business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OfferDetailResourceTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.detail = create_offer(self.business).details.get(offer_type="basic")
        self.url = reverse("offerdetail-detail", args=[self.detail.id])

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_full_detail(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {
                "id",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
            },
        )

    def test_unknown_detail_returns_404(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("offerdetail-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
