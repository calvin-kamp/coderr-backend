from rest_framework.permissions import BasePermission

from accounts.models import User


class IsCustomerUser(BasePermission):
    message = "Only customer users can create orders."

    def has_permission(self, request, view):
        return request.user.type == User.RoleChoices.CUSTOMER


class IsOrderBusinessUser(BasePermission):
    message = "Only the business user of this order can update its status."

    def has_permission(self, request, view):
        return request.user.type == User.RoleChoices.BUSINESS

    def has_object_permission(self, request, view, obj):
        return obj.business_user_id == request.user.id


class IsStaffUser(BasePermission):
    message = "Only admin users can delete orders."

    def has_permission(self, request, view):
        return request.user.is_staff
