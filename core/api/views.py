from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile, User
from offers.models import Offer
from reviews.models import Review


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
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
