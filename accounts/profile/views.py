"""Views for the profile endpoints.

Two rules recur in this module:
  * The URL parameter is the **user** id, not the profile id. ``lookup_field``
    is set to ``user_id`` so ``/api/profile/5/`` addresses the profile of user 5,
    which is what the frontend has at hand after login.
  * Every queryset uses ``select_related("user")``, because each serialized
    profile reads several fields off its user.

Contents:
  * ProfileDetailView       -- /api/profile/<pk>/, readable by anyone logged in,
                               writable only by the owner.
  * BusinessProfileListView -- /api/profiles/business/, unpaginated list.
  * CustomerProfileListView -- /api/profiles/customer/, unpaginated list.
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.models import Profile, User

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    ProfileSerializer,
)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Return a single profile and let its owner update it.

    ``RetrieveUpdateAPIView`` would also route PUT. Only a partial update is
    offered here, so PUT is dropped from ``http_method_names`` and answered with
    405.
    """

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "head", "options"]


class BusinessProfileListView(generics.ListAPIView):
    """List every business profile as a bare array.

    Pagination is switched off because the frontend renders the full list.
    """

    queryset = Profile.objects.select_related("user").filter(
        user__type=User.RoleChoices.BUSINESS
    )
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class CustomerProfileListView(generics.ListAPIView):
    """List every customer profile as a bare array."""

    queryset = Profile.objects.select_related("user").filter(
        user__type=User.RoleChoices.CUSTOMER
    )
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
