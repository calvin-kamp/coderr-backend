"""Views for the order endpoints.

Two rules recur in this module:
  * Permissions per action: creating, updating and deleting are each restricted
    to a different role, so ``get_permissions`` swaps the classes instead of
    putting every rule into one permission class.
  * Queryset per action: the list route is narrowed to the orders the user is
    party to, while the single-object actions keep the full queryset so the
    permission classes answer with 403 rather than hiding the order behind a 404.

Contents:
  * OrderViewSet            -- /api/orders/ and /api/orders/<id>/. Customers
                               create, the business user of the order updates
                               its status, only staff may delete.
  * BaseOrderCountView      -- shared implementation of the two count routes.
  * OrderCountView          -- /api/order-count/<business_user_id>/, in progress.
  * CompletedOrderCountView -- /api/completed-order-count/<business_user_id>/.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from orders.models import Order

from .permissions import IsCustomerUser, IsOrderBusinessUser, IsStaffUser
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    """List, create, update and delete orders.

    Pagination is switched off because the response is a bare array, and PUT is
    dropped from ``http_method_names`` because only a partial update is offered.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Return the orders the current action is allowed to address.

        A user sees an order if they are on either side of it. For update and
        delete the queryset stays unfiltered on purpose: the permission classes
        decide, and a foreign order has to come back as 403 -- filtering it out
        here would turn that into a misleading 404.
        """
        if self.action in ("partial_update", "destroy"):
            return Order.objects.all()

        user = self.request.user

        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def get_permissions(self):
        """Return the permission classes for the current action."""
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]

        if self.action == "partial_update":
            return [IsAuthenticated(), IsOrderBusinessUser()]

        if self.action == "destroy":
            return [IsAuthenticated(), IsStaffUser()]

        return super().get_permissions()

    def get_serializer_class(self):
        """Pick the serializer that matches the input the action accepts."""
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "partial_update":
            return OrderStatusSerializer

        return OrderSerializer


class BaseOrderCountView(APIView):
    """Shared logic of the two order count endpoints.

    Both routes differ only in the status they count and the key they return it
    under, so the subclasses set those two attributes and inherit ``get``.
    """

    permission_classes = [IsAuthenticated]
    order_status = None
    response_key = None

    def get(self, request, business_user_id):
        """Count this business user's orders in the configured status.

        The lookup filters on ``type`` as well, so a customer id yields a 404
        instead of a count of zero.
        """
        business_user = get_object_or_404(
            User, pk=business_user_id, type=User.RoleChoices.BUSINESS
        )
        count = Order.objects.filter(
            business_user=business_user, status=self.order_status
        ).count()

        return Response({self.response_key: count}, status=status.HTTP_200_OK)


class OrderCountView(BaseOrderCountView):
    """Number of orders a business user currently has in progress."""

    order_status = Order.StatusChoices.IN_PROGRESS
    response_key = "order_count"


class CompletedOrderCountView(BaseOrderCountView):
    """Number of orders a business user has completed."""

    order_status = Order.StatusChoices.COMPLETED
    response_key = "completed_order_count"
