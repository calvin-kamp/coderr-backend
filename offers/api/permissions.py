"""Permission classes for the offer endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class IsBusinessUserOrReadOnly(BasePermission):
    """Read for everyone, write for business users, edit for the owner.

    The check runs in two stages: ``has_permission`` filters out customer users
    before an object is even fetched, ``has_object_permission`` then narrows it
    down to the owner of the offer.
    """

    message = "Only business users can create or edit offers."

    def has_permission(self, request, view):
        """Allow safe methods for anyone, writes only for business users."""
        if request.method in SAFE_METHODS:
            return True

        return request.user.type == User.RoleChoices.BUSINESS

    def has_object_permission(self, request, view, obj):
        """Allow safe methods for anyone, writes only for the offer owner.

        The message is overwritten first, so the 403 body names the actual
        reason: the caller is a business user, just not this offer's owner.
        """
        if request.method in SAFE_METHODS:
            return True

        self.message = "You can only edit your own offers."
        return obj.user_id == request.user.id
