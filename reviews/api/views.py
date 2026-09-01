"""Views for the review endpoints.

The whole resource is one view set. Its rules are expressed through two
permission classes stacked on top of ``IsAuthenticated``: one decides who may
write at all, the other who may touch an existing review. Reading stays open to
every authenticated user, which is why both classes let the safe methods pass.

Contents:
  * ReviewViewSet -- /api/reviews/ and /api/reviews/<id>/. Customers create,
                     the author edits and deletes, everyone logged in may read.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from reviews.models import Review

from .filters import ReviewFilter
from .permissions import IsCustomerUserOrReadOnly, IsReviewerOrReadOnly
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """List, create, update and delete reviews.

    Pagination is switched off because the response is a bare array, and PUT is
    dropped from ``http_method_names`` because only a partial update is offered.
    """

    queryset = Review.objects.select_related("business_user", "reviewer")
    permission_classes = [
        IsAuthenticated,
        IsCustomerUserOrReadOnly,
        IsReviewerOrReadOnly,
    ]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Use the restricted serializer for updates, the full one otherwise."""
        if self.action == "partial_update":
            return ReviewUpdateSerializer

        return ReviewSerializer
