"""Permission classes for the review endpoints.

Both classes let the safe methods through, because every authenticated user may
read reviews regardless of role or authorship.

Contents:
  * IsCustomerUserOrReadOnly -- who may write a review at all.
  * IsReviewerOrReadOnly     -- who may change an existing one.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class IsCustomerUserOrReadOnly(BasePermission):
    """Only customer accounts may write reviews."""

    message = "Only customer users can create reviews."

    def has_permission(self, request, view):
        """Allow safe methods for anyone, writes only for customers."""
        if request.method in SAFE_METHODS:
            return True

        return request.user.type == User.RoleChoices.CUSTOMER


class IsReviewerOrReadOnly(BasePermission):
    """Only the author may edit or delete a review.

    Only ``has_object_permission`` is implemented, so a foreign review is
    answered with 403 rather than being hidden behind a 404.
    """

    message = "You can only edit your own reviews."

    def has_object_permission(self, request, view, obj):
        """Allow safe methods for anyone, writes only for the author."""
        if request.method in SAFE_METHODS:
            return True

        return obj.reviewer_id == request.user.id
