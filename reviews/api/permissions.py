from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class IsCustomerUserOrReadOnly(BasePermission):
    message = "Only customer users can create reviews."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.type == User.RoleChoices.CUSTOMER


class IsReviewerOrReadOnly(BasePermission):
    message = "You can only edit your own reviews."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.reviewer_id == request.user.id
