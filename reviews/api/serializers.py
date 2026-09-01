"""Serializers for the review endpoints.

Contents:
  * ReviewSerializer       -- read representation and create input.
  * ReviewUpdateSerializer -- rating and description only, for partial updates.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from accounts.models import User
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Read a review, or create one for the requesting customer.

    ``reviewer`` is read-only so a client cannot review in someone else's name.
    Its ``CurrentUserDefault`` still supplies the requesting user, which is what
    the ``UniqueTogetherValidator`` needs in order to check the pair before
    ``create`` ever runs.
    """

    reviewer = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        """Expose every review field and turn the unique pair into a 400.

        The ``UniqueTogetherValidator`` mirrors the model constraint so a repeat
        review comes back as a readable validation error instead of a database
        error.
        """

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
        """Reject a review aimed at a customer account."""
        if value.type != User.RoleChoices.BUSINESS:
            raise serializers.ValidationError("This user is not a business user.")

        return value

    def create(self, validated_data):
        """Attach the requesting user as the reviewer."""
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Update nothing but the rating and the description."""

    class Meta:
        """Expose the two editable fields."""

        model = Review
        fields = ("rating", "description")

    def validate(self, attrs):
        """Reject any field other than the two editable ones.

        DRF would silently ignore unknown keys, so an attempt to move the review
        to a different business user would answer 200 and change nothing.
        """
        unknown = set(self.initial_data) - set(self.fields)

        if unknown:
            raise serializers.ValidationError(
                {field: "This field is not editable." for field in unknown}
            )

        return attrs

    def to_representation(self, instance):
        """Answer with the full review, not just the two changed fields."""
        return ReviewSerializer(instance, context=self.context).data
