from django.urls import reverse, reverse_lazy
from rest_framework import status

from accounts.models import User
from accounts.tests.utils import BaseAPITestCase, create_user
from offers.tests import create_offer
from orders.models import Order


def create_order(customer, business, **overrides):
    data = {
        "customer_user": customer,
        "business_user": business,
        "title": "Logo Design",
        "revisions": 3,
        "delivery_time_in_days": 5,
        "price": 150,
        "features": ["Logo Design"],
        "offer_type": "basic",
    }
    data.update(overrides)
    return Order.objects.create(**data)


class OrderListTests(BaseAPITestCase):
    url = reverse_lazy("order-list")

    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.stranger = create_user("stranger", User.RoleChoices.CUSTOMER)
        self.order = create_order(self.customer, self.business)

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_sees_own_orders(self):
        self.authenticate(self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            set(response.data[0]),
            {
                "id",
                "customer_user",
                "business_user",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
                "status",
                "created_at",
                "updated_at",
            },
        )

    def test_business_sees_received_orders(self):
        self.authenticate(self.business)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.id)

    def test_uninvolved_user_sees_nothing(self):
        self.authenticate(self.stranger)
        response = self.client.get(self.url)
        self.assertEqual(response.data, [])


class OrderCreateTests(BaseAPITestCase):
    url = reverse_lazy("order-list")

    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.detail = create_offer(self.business).details.get(offer_type="basic")

    def test_customer_can_create_order_from_offer_detail(self):
        self.authenticate(self.customer)
        response = self.client.post(
            self.url, {"offer_detail_id": self.detail.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["price"], self.detail.price)
        self.assertEqual(response.data["offer_type"], "basic")
        self.assertEqual(response.data["status"], "in_progress")

    def test_business_user_is_forbidden(self):
        self.authenticate(self.business)
        response = self.client.post(
            self.url, {"offer_detail_id": self.detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_offer_detail_id_returns_400(self):
        self.authenticate(self.customer)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_offer_detail_id_returns_404(self):
        self.authenticate(self.customer)
        response = self.client.post(self.url, {"offer_detail_id": 9999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderUpdateTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.other_business = create_user("biz2", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.order = create_order(self.customer, self.business)
        self.url = reverse("order-detail", args=[self.order.id])

    def test_business_owner_can_update_status(self):
        self.authenticate(self.business)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["id"], self.order.id)

    def test_customer_cannot_update_status(self):
        self.authenticate(self.customer)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_business_user_cannot_update_status(self):
        self.authenticate(self.other_business)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_status_returns_400(self):
        self.authenticate(self.business)
        response = self.client.patch(self.url, {"status": "done"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_editable_field_returns_400(self):
        self.authenticate(self.business)
        response = self.client.patch(self.url, {"price": 1}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_unknown_order_returns_404(self):
        self.authenticate(self.business)
        response = self.client.patch(
            reverse("order-detail", args=[9999]),
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDeleteTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        self.staff = create_user("admin_user", User.RoleChoices.BUSINESS)
        self.staff.is_staff = True
        self.staff.save(update_fields=["is_staff"])
        self.order = create_order(self.customer, self.business)
        self.url = reverse("order-detail", args=[self.order.id])

    def test_staff_can_delete(self):
        self.authenticate(self.staff)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.id).exists())

    def test_business_user_cannot_delete(self):
        self.authenticate(self.business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_delete(self):
        self.authenticate(self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderCountTests(BaseAPITestCase):
    def setUp(self):
        self.business = create_user("biz", User.RoleChoices.BUSINESS)
        self.customer = create_user("cust", User.RoleChoices.CUSTOMER)
        create_order(self.customer, self.business)
        create_order(self.customer, self.business)
        create_order(self.customer, self.business, status="completed")

    def test_requires_authentication(self):
        response = self.client.get(reverse("order-count", args=[self.business.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_counts_in_progress_orders(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("order-count", args=[self.business.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_count": 2})

    def test_counts_completed_orders(self):
        self.authenticate(self.customer)
        response = self.client.get(
            reverse("completed-order-count", args=[self.business.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"completed_order_count": 1})

    def test_non_business_user_returns_404(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("order-count", args=[self.customer.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unknown_user_returns_404(self):
        self.authenticate(self.customer)
        response = self.client.get(reverse("completed-order-count", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
