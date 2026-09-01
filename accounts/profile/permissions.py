"""Permission classes for the profile endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow reading any profile, but writing only to its owner.

    Only ``has_object_permission`` is implemented, so the check runs after the
    object has been fetched and a foreign profile is answered with 403 rather
    than being hidden behind a 404.
    """

    message = "You can only edit your own profile."

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods, otherwise only for the owner."""
        if request.method in SAFE_METHODS:
            return True

        return obj.user_id == request.user.id
