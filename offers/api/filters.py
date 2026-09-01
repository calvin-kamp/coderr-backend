"""Filter set for the offer list endpoint."""

from django_filters import rest_framework as filters

from offers.models import Offer


class OfferFilter(filters.FilterSet):
    """Query parameters of the offer list.

    None of the three filters matches its own name on the model, so all of them
    are declared explicitly:

      * ``creator_id`` addresses the owning user through ``user_id``.
      * ``min_price`` and ``max_delivery_time`` filter the annotations
        ``min_price`` and ``min_delivery_time`` that the view adds to the
        queryset -- the offer itself has no price and no delivery time.
    """

    creator_id = filters.NumberFilter(field_name="user_id")
    min_price = filters.NumberFilter(field_name="min_price", lookup_expr="gte")
    max_delivery_time = filters.NumberFilter(
        field_name="min_delivery_time", lookup_expr="lte"
    )

    class Meta:
        """Bind the three declared filters to the offer model."""

        model = Offer
        fields = ("creator_id", "min_price", "max_delivery_time")
