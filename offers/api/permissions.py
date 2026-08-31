from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class IsBusinessUserOrReadOnly(BasePermission):
    message = "Only business users can create or edit offers."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.type == User.RoleChoices.BUSINESS

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        self.message = "You can only edit your own offers."
        return obj.user_id == request.user.id
