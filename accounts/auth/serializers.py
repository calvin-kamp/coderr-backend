from django.contrib.auth import authenticate, password_validation
from django.db import transaction
from rest_framework import serializers

from accounts.models import Profile, User


class RegisterSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "type",
            "password",
            "repeated_password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "type": {"required": True},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            Profile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError("Invalid login credentials.")

        attrs["user"] = user
        return attrs
