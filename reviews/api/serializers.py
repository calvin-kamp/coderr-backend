from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from accounts.models import User
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=("business_user", "reviewer"),
                message="You have already reviewed this business user.",
            )
        ]

    def validate_business_user(self, value):
        if value.type != User.RoleChoices.BUSINESS:
            raise serializers.ValidationError("This user is not a business user.")

        return value

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("rating", "description")

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)

        if unknown:
            raise serializers.ValidationError(
                {field: "This field is not editable." for field in unknown}
            )

        return attrs

    def to_representation(self, instance):
        return ReviewSerializer(instance, context=self.context).data
