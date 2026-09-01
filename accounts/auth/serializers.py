"""Serializers for registration and login.

Contents:
  * RegisterSerializer -- validates the sign-up payload and creates the user
                          together with its profile.
  * LoginSerializer    -- plain serializer that turns credentials into a user.
"""

from django.contrib.auth import authenticate, password_validation
from django.db import transaction
from rest_framework import serializers

from accounts.models import Profile, User


class RegisterSerializer(serializers.ModelSerializer):
    """Create a new business or customer account.

    ``repeated_password`` is not a model field, so it is declared explicitly and
    only used for the comparison in ``validate``.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """Expose the sign-up fields and keep both passwords write-only."""

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
        """Run the validators configured in ``AUTH_PASSWORD_VALIDATORS``."""
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        """Reject the payload when both password fields differ."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create the user and its profile as one unit.

        Both writes belong together: without the atomic block a failure while
        creating the profile would leave behind a user that has none, and the
        profile views assume every user has exactly one.
        """
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            Profile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """Validate credentials and expose the authenticated user."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the credentials and attach the user to ``attrs``.

        ``authenticate`` returns ``None`` for an unknown username and for a
        wrong password alike. The error message stays generic on purpose so the
        response does not reveal which usernames exist.
        """
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError("Invalid login credentials.")

        attrs["user"] = user
        return attrs
