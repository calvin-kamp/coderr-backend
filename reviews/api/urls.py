"""URL routes for the review endpoints.

The router covers ``/api/reviews/`` and ``/api/reviews/<id>/``; there are no
extra routes to add by hand.
"""

from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = router.urls
