"""Serializers for the offer endpoints.

The same offer is represented in three different shapes, which is why there are
several serializers instead of one:

  * the list adds ``user_details`` and links to the detail rows,
  * the retrieve route drops ``user_details`` but keeps the links,
  * create and update send and return the detail rows in full.

Contents:
  * OfferDetailSerializer       -- a full package tier.
  * OfferDetailLinkSerializer   -- id plus hyperlink, used inside the read views.
  * OfferUserSerializer         -- the three owner fields shown in the list.
  * OfferRetrieveSerializer     -- single offer with detail links.
  * OfferListSerializer         -- the same plus ``user_details``.
  * OfferCreateUpdateSerializer -- writable offer with nested details.
"""

from django.db import transaction
from rest_framework import serializers

from accounts.models import User
from offers.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """A package tier with all of its fields."""

    class Meta:
        """Expose every tier field the API reads or writes."""

        model = OfferDetail
        fields = (
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        )


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """A package tier reduced to its id and its own URL.

    ``view_name`` points at the route name of ``OfferDetailRetrieveView``, so
    the link stays correct if the URL path ever changes.
    """

    url = serializers.HyperlinkedIdentityField(view_name="offerdetail-detail")

    class Meta:
        """Expose the id and the generated hyperlink."""

        model = OfferDetail
        fields = ("id", "url")


class OfferUserSerializer(serializers.ModelSerializer):
    """The owner fields the offer list displays next to each offer."""

    class Meta:
        """Expose the owner's name and username."""

        model = User
        fields = ("first_name", "last_name", "username")


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Single offer with links to its package tiers.

    ``min_price`` and ``min_delivery_time`` are declared read-only rather than
    as model fields: they do not exist on the model and are supplied by the
    annotations in ``OfferViewSet.get_queryset``.
    """

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.IntegerField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        """Expose the offer fields plus the two aggregated values."""

        model = Offer
        fields = (
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        )


class OfferListSerializer(OfferRetrieveSerializer):
    """List representation: the retrieve fields plus the owner block."""

    user_details = OfferUserSerializer(source="user", read_only=True)

    class Meta(OfferRetrieveSerializer.Meta):
        """Extend the inherited field list by ``user_details``."""

        fields = OfferRetrieveSerializer.Meta.fields + ("user_details",)


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for creating and updating an offer with its details."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        """Expose the writable offer fields and the nested tier list."""

        model = Offer
        fields = ("id", "title", "image", "description", "details")

    def validate_details(self, value):
        """Check the tier list for duplicates and, on create, for completeness.

        Every tier has to name its ``offer_type``, because that is what
        ``update`` matches an incoming tier against an existing row by. The model
        field has a default, so DRF would otherwise leave the key out of
        ``validated_data`` entirely.

        ``self.instance is None`` distinguishes the two cases: a new offer needs
        all three tiers, while an update may carry a single one.
        """
        if any(detail.get("offer_type") is None for detail in value):
            raise serializers.ValidationError("Each detail requires an offer_type.")

        types = [detail["offer_type"] for detail in value]

        if len(types) != len(set(types)):
            raise serializers.ValidationError("Each offer_type may only appear once.")

        if self.instance is None and set(types) != set(OfferDetail.OfferChoices.values):
            raise serializers.ValidationError(
                "An offer requires exactly three details: basic, standard and premium."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create the offer and its three tiers in one transaction.

        The offer alone is not a valid state -- if one of the tiers failed to be
        written, the API would hand out an offer without any pricing. The
        transaction makes both writes succeed or fail together.
        """
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user, **validated_data
        )
        OfferDetail.objects.bulk_create(
            OfferDetail(offer=offer, **detail) for detail in details_data
        )
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update the offer fields and the tiers that were sent along.

        Tiers are matched by ``offer_type``, not by id, so every tier in the
        payload has to carry its type. ``update_or_create`` then keeps the
        existing row and its id when that type is already present.

        A ``details`` value of ``None`` means the client sent no such key at all
        and the existing tiers stay untouched.
        """
        details_data = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for detail_data in details_data:
                OfferDetail.objects.update_or_create(
                    offer=instance,
                    offer_type=detail_data.pop("offer_type"),
                    defaults=detail_data,
                )

        return instance

    def to_representation(self, instance):
        """Return the full tier objects instead of the input representation.

        Without this override the response would echo back only what was sent,
        so updating a single tier would answer with a one-element list. The
        response always contains all three tiers in full.
        """
        data = super().to_representation(instance)
        data["details"] = OfferDetailSerializer(instance.details.all(), many=True).data
        return data
