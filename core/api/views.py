"""View for the cross-app base info endpoint.

This is the only endpoint that aggregates across apps and belongs to none of
them, which is why it lives in ``core`` instead of in ``reviews`` or ``offers``.

Contents:
  * BaseInfoView -- GET /api/base-info/, public platform statistics.
"""

from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile, User
from offers.models import Offer
from reviews.models import Review


class BaseInfoView(APIView):
    """Return the four counters the landing page displays.

    ``AllowAny`` overrides the project-wide ``IsAuthenticated`` default, because
    the numbers are shown to visitors who are not signed in.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """Aggregate reviews, business profiles and offers into one response.

        ``Avg`` returns ``None`` on an empty table, which would serialize as
        ``null``; the frontend expects a number, so the average falls back to
        ``0.0`` and is otherwise rounded to one decimal place.
        """
        average_rating = Review.objects.aggregate(average=Avg("rating"))["average"]

        return Response(
            {
                "review_count": Review.objects.count(),
                "average_rating": (
                    round(average_rating, 1) if average_rating is not None else 0.0
                ),
                "business_profile_count": Profile.objects.filter(
                    user__type=User.RoleChoices.BUSINESS
                ).count(),
                "offer_count": Offer.objects.count(),
            },
            status=status.HTTP_200_OK,
        )
