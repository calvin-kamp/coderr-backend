"""Serializers for the profile endpoints.

The profile is split across two tables: ``username``, ``first_name``,
``last_name``, ``email`` and ``type`` live on the user, everything else on the
profile. The serializers pull the user fields in via ``source="user.<field>"``
so the API can present both tables as one flat object.

Contents:
  * ProfileSerializer         -- full representation for a single profile.
  * BusinessProfileSerializer -- field subset for the business list.
  * CustomerProfileSerializer -- field subset for the customer list.
"""

from rest_framework import serializers

from accounts.models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    """Read and update a single profile including its user fields."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True
    )
    email = serializers.EmailField(source="user.email", required=False)
    type = serializers.CharField(source="user.type", read_only=True)

    class Meta:
        """Flat field list spanning both tables; identity fields stay read-only."""

        model = Profile
        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        )
        read_only_fields = ("user", "created_at")

    def validate_email(self, value):
        """Reject an address that another account already uses.

        The uniqueness check has to be written out because ``email`` is a
        declared field with a ``source``, which means the automatic unique
        validator of the model does not apply here.

        On update the own user is excluded, otherwise resubmitting the unchanged
        address would count as a collision with itself.
        """
        queryset = User.objects.filter(email__iexact=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.user_id)

        if queryset.exists():
            raise serializers.ValidationError("This email address is already in use.")

        return value

    def update(self, instance, validated_data):
        """Write the user fields to the user and the rest to the profile.

        Because of the ``source="user.<field>"`` declarations, DRF nests those
        values under a ``user`` key in ``validated_data``. They have to be
        popped and saved separately -- ``super().update`` would try to set them
        on the profile.
        """
        user_data = validated_data.pop("user", {})

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save(update_fields=list(user_data.keys()))

        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    """Business list representation: everything except email and timestamp."""

    class Meta(ProfileSerializer.Meta):
        """Narrow the inherited field list to what the business list shows."""

        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        )


class CustomerProfileSerializer(ProfileSerializer):
    """Customer list representation: only the fields the frontend displays."""

    class Meta(ProfileSerializer.Meta):
        """Narrow the inherited field list to what the customer list shows."""

        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "type",
        )
