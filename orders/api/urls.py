"""URL routes for the order endpoints.

The router covers ``/api/orders/`` and ``/api/orders/<id>/``. The two count
routes are added by hand: they are aggregates, not a resource the router could
derive from the view set.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CompletedOrderCountView, OrderCountView, OrderViewSet

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = router.urls + [
    path(
        "order-count/<int:business_user_id>/",
        OrderCountView.as_view(),
        name="order-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]
