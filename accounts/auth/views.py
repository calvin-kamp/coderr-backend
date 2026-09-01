"""Views for the registration and login endpoints.

Two rules recur in this module:
  * Both views override the project-wide ``IsAuthenticated`` default with
    ``AllowAny``, because a caller who has no account yet cannot authenticate.
  * Both assemble their response by hand instead of returning ``serializer.data``,
    since the body carries the auth token next to the user fields and names the
    primary key ``user_id``.

Contents:
  * RegisterView -- POST /api/registration/, creates the account and its token.
  * LoginView    -- POST /api/login/, returns the token of an existing account.
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(APIView):
    """Create a new user account and hand out its first token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a user and return the auth token with 201."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate an existing user and return the auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate the credentials and return the auth token with 200.

        ``get_or_create`` rather than ``create``: token authentication keeps one
        long-lived token per user, so signing in again returns the same key.
        """
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )
