from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BusinessListView, CustomerListView, ProfileViewSet

router = DefaultRouter()
router.register(r"profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("profiles/business/", BusinessListView.as_view(), name="business-list"),
    path("profiles/customer/", CustomerListView.as_view(), name="customer-list"),
] + router.urls
