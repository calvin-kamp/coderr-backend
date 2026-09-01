"""Permission classes for the order endpoints.

The three roles the order routes distinguish get one class each, so
``OrderViewSet.get_permissions`` can combine them per action.

Contents:
  * IsCustomerUser      -- may place orders.
  * IsOrderBusinessUser -- may change the status of their own orders.
  * IsStaffUser         -- may delete orders.
"""

from rest_framework.permissions import BasePermission

from accounts.models import User


class IsCustomerUser(BasePermission):
    """Only customer accounts may place orders."""

    message = "Only customer users can create orders."

    def has_permission(self, request, view):
        """Return whether the requesting user is a customer."""
        return request.user.type == User.RoleChoices.CUSTOMER


class IsOrderBusinessUser(BasePermission):
    """Only the business user of an order may change its status.

    The check is split in two: ``has_permission`` rejects customers before the
    order is fetched, ``has_object_permission`` then rejects business users who
    are not party to this particular order.
    """

    message = "Only the business user of this order can update its status."

    def has_permission(self, request, view):
        """Return whether the requesting user is a business user at all."""
        return request.user.type == User.RoleChoices.BUSINESS

    def has_object_permission(self, request, view, obj):
        """Return whether the order was placed with this business user."""
        return obj.business_user_id == request.user.id


class IsStaffUser(BasePermission):
    """Only admin accounts may delete orders."""

    message = "Only admin users can delete orders."

    def has_permission(self, request, view):
        """Return whether the requesting user has staff rights."""
        return request.user.is_staff
