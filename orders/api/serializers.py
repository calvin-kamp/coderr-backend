from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers.models import OfferDetail
from orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
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
    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
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
        return OrderSerializer(instance, context=self.context).data


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status",)

    def validate(self, attrs):
        unknown = set(self.initial_data) - {"status"}

        if unknown:
            raise serializers.ValidationError(
                {field: "This field is not editable." for field in unknown}
            )

        return attrs

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
