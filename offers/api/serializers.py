from django.db import transaction
from rest_framework import serializers

from accounts.models import User
from offers.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
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
    url = serializers.HyperlinkedIdentityField(view_name="offerdetail-detail")

    class Meta:
        model = OfferDetail
        fields = ("id", "url")


class OfferUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")


class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.IntegerField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
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
    user_details = OfferUserSerializer(source="user", read_only=True)

    class Meta(OfferRetrieveSerializer.Meta):
        fields = OfferRetrieveSerializer.Meta.fields + ("user_details",)


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ("id", "title", "image", "description", "details")

    def validate_details(self, value):
        types = [detail.get("offer_type") for detail in value]

        if len(types) != len(set(types)):
            raise serializers.ValidationError("Each offer_type may only appear once.")

        if self.instance is None and set(types) != set(OfferDetail.OfferChoices.values):
            raise serializers.ValidationError(
                "An offer requires exactly three details: basic, standard and premium."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
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
        data = super().to_representation(instance)
        data["details"] = OfferDetailSerializer(instance.details.all(), many=True).data
        return data
