from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers

from accounts.models import Profile, User


class RegisterSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = ("id", "username", "email", "password", "repeated_password")

        extra_kwargs = {
            "password": {
                "write_only": True,
            },
            "type": {"required": True, "write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")
        type = validated_data.pop("type")
        validated_data.pop("repeated_password")

        with transaction.atomic():
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()

            Profile.objects.create(user=user, email=user.email, type=type)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])

        if not user:
            raise serializers.ValidationError("Invalid Login credentials")

        attrs["user"] = user

        return attrs
