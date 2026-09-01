"""Views for the offer endpoints.

Two rules recur in this module:
  * Serializer per action: ``get_serializer_class`` picks the serializer that
    matches the response shape of the route -- the list carries the owner block,
    the retrieve route does not, and writes exchange the full tier objects.
  * Annotated queryset: ``min_price`` and ``min_delivery_time`` are computed by
    the database instead of in Python, because the list route also has to filter
    and sort by them.

Contents:
  * OfferViewSet            -- /api/offers/ and /api/offers/<id>/. Anyone logged
                               in may read, business users may create, only the
                               owner may edit or delete.
  * OfferDetailRetrieveView -- /api/offerdetails/<id>/, read-only single tier.
"""

from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from offers.models import Offer, OfferDetail

from .filters import OfferFilter
from .paginations import OfferListPagination
from .permissions import IsBusinessUserOrReadOnly
from .serializers import (
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """List, create, read, update and delete offers.

    PUT is dropped from ``http_method_names`` because only a partial update is
    offered; a PUT request is answered with 405.
    """

    permission_classes = [IsAuthenticated, IsBusinessUserOrReadOnly]
    pagination_class = OfferListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Return every offer, annotated with its cheapest and fastest tier.

        The annotations have to exist before the filter backends run, since
        ``OfferFilter`` and the ordering both address ``min_price`` and
        ``min_delivery_time``.
        """
        return (
            Offer.objects.select_related("user")
            .prefetch_related("details")
            .annotate(
                min_price=Min("details__price"),
                min_delivery_time=Min("details__delivery_time_in_days"),
            )
        )

    def get_serializer_class(self):
        """Pick the serializer that matches the response shape of the action."""
        if self.action == "list":
            return OfferListSerializer
        if self.action == "retrieve":
            return OfferRetrieveSerializer
        return OfferCreateUpdateSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Return a single package tier.

    This is the target of the ``url`` field the read serializers put into each
    entry of ``details``.
    """

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
