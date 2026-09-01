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
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if self.action in ("partial_update", "destroy"):
            return Order.objects.all()

        user = self.request.user

        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]

        if self.action == "partial_update":
            return [IsAuthenticated(), IsOrderBusinessUser()]

        if self.action == "destroy":
            return [IsAuthenticated(), IsStaffUser()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "partial_update":
            return OrderStatusSerializer

        return OrderSerializer


class BaseOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    order_status = None
    response_key = None

    def get(self, request, business_user_id):
        business_user = get_object_or_404(
            User, pk=business_user_id, type=User.RoleChoices.BUSINESS
        )
        count = Order.objects.filter(
            business_user=business_user, status=self.order_status
        ).count()

        return Response({self.response_key: count}, status=status.HTTP_200_OK)


class OrderCountView(BaseOrderCountView):
    order_status = Order.StatusChoices.IN_PROGRESS
    response_key = "order_count"


class CompletedOrderCountView(BaseOrderCountView):
    order_status = Order.StatusChoices.COMPLETED
    response_key = "completed_order_count"
