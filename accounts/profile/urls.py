"""URL routes for the profile endpoints.

Included under the ``api/`` prefix in ``core.urls``. The detail route is
singular (``profile/``) while the two list routes are plural (``profiles/``).
"""

from django.urls import path

from .views import BusinessProfileListView, CustomerProfileListView, ProfileDetailView

urlpatterns = [
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/business/", BusinessProfileListView.as_view(), name="business-list"),
    path("profiles/customer/", CustomerProfileListView.as_view(), name="customer-list"),
]
