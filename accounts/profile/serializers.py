from rest_framework import serializers

from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        )
        extra_kwargs = {
            "username": {"read_only": True},
            "type": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def get_username(self, obj):
        return obj.user.username


class BusinessProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        )
        extra_kwargs = {
            "username": {"read_only": True},
            "type": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def get_username(self, obj):
        return obj.user.username


class CustomerProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user",
            "username",
            "first_name",
            "last_name",
            "type",
        )
        extra_kwargs = {
            "username": {"read_only": True},
            "type": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def get_username(self, obj):
        return obj.user.username
