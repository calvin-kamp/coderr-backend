from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from accounts.models import Profile

from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    ProfileSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]


class BusinessListView(ListAPIView):
    queryset = Profile.objects.filter(type="business")
    serializer_class = BusinessProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return super().get_queryset()


class CustomerListView(ListAPIView):
    queryset = Profile.objects.filter(type="customer")
    serializer_class = CustomerProfileSerializer
    permission_classes = [AllowAny]
