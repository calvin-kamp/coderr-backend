"""Pagination for the offer list endpoint."""

from rest_framework.pagination import PageNumberPagination


class OfferListPagination(PageNumberPagination):
    """Page-number pagination with a client-adjustable page size.

    The default of six matches the offer grid in the frontend; ``page_size``
    lets the client ask for a different number, capped at 100.
    """

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
