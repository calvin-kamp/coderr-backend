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
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "head", "options"]


class BusinessProfileListView(generics.ListAPIView):
    queryset = Profile.objects.select_related("user").filter(
        user__type=User.RoleChoices.BUSINESS
    )
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class CustomerProfileListView(generics.ListAPIView):
    queryset = Profile.objects.select_related("user").filter(
        user__type=User.RoleChoices.CUSTOMER
    )
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
