"""Serializers for the order endpoints.

Reads and writes are deliberately asymmetric here: a client posts a single
``offer_detail_id`` and patches a single ``status``, but both responses are the
complete order. The two write serializers therefore hand the rendering back to
``OrderSerializer`` in ``to_representation``.

Contents:
  * OrderSerializer       -- read representation, used for list and retrieve.
  * OrderCreateSerializer -- takes a tier id and copies it into a new order.
  * OrderStatusSerializer -- status-only update.
"""

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers.models import OfferDetail
from orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Full read representation of an order."""

    class Meta:
        """Expose every order field."""

        model = Order
        fields = (
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        )


class OrderCreateSerializer(serializers.Serializer):
    """Create an order from a package tier.

    A plain ``Serializer`` rather than a ``ModelSerializer``: the only input is
    an id, and every field of the order is derived from it instead of being sent
    by the client.
    """

    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        """Copy the package tier into a new order.

        ``get_object_or_404`` raises ``Http404``, which DRF turns into a 404 for
        an unknown ``offer_detail_id``.

        The values are copied, not referenced, so the order keeps the terms that
        were agreed on even if the offer is edited or deleted later.
        """
        offer_detail = get_object_or_404(
            OfferDetail.objects.select_related("offer__user"),
            pk=validated_data["offer_detail_id"],
        )

        return Order.objects.create(
            customer_user=self.context["request"].user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=list(offer_detail.features),
            offer_type=offer_detail.offer_type,
        )

    def to_representation(self, instance):
        """Answer with the full order instead of the ``offer_detail_id`` input."""
        return OrderSerializer(instance, context=self.context).data


class OrderStatusSerializer(serializers.ModelSerializer):
    """Update nothing but the status of an order."""

    class Meta:
        """Expose the status as the only writable field."""

        model = Order
        fields = ("status",)

    def validate(self, attrs):
        """Reject any field other than ``status``.

        DRF would silently ignore unknown keys, so a client trying to change the
        price would get a 200 and no effect. ``initial_data`` holds the raw
        payload, which is what makes the comparison possible.
        """
        unknown = set(self.initial_data) - {"status"}

        if unknown:
            raise serializers.ValidationError(
                {field: "This field is not editable." for field in unknown}
            )

        return attrs

    def to_representation(self, instance):
        """Answer with the full order, not just the changed status."""
        return OrderSerializer(instance, context=self.context).data
