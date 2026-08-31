from rest_framework import serializers

from accounts.models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
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
        queryset = User.objects.filter(email__iexact=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.user_id)

        if queryset.exists():
            raise serializers.ValidationError("This email address is already in use.")

        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save(update_fields=list(user_data.keys()))

        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
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
    class Meta(ProfileSerializer.Meta):
        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "type",
        )
