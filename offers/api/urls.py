"""URL routes for the offer endpoints.

The router covers ``/api/offers/`` and ``/api/offers/<id>/``. The tier route is
added by hand because ``/api/offerdetails/<id>/`` is a separate resource and not
nested under an offer; its name ``offerdetail-detail`` is what
``OfferDetailLinkSerializer`` reverses to build the hyperlinks.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OfferDetailRetrieveView, OfferViewSet

router = DefaultRouter()
router.register(r"offers", OfferViewSet, basename="offer")

urlpatterns = router.urls + [
    path(
        "offerdetails/<int:pk>/",
        OfferDetailRetrieveView.as_view(),
        name="offerdetail-detail",
    ),
]
