from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from reviews.models import Review

from .filters import ReviewFilter
from .permissions import IsCustomerUserOrReadOnly, IsReviewerOrReadOnly
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("business_user", "reviewer")
    permission_classes = [
        IsAuthenticated,
        IsCustomerUserOrReadOnly,
        IsReviewerOrReadOnly,
    ]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return ReviewUpdateSerializer

        return ReviewSerializer
