"""Filter set for the review list endpoint."""

from django_filters import rest_framework as filters

from reviews.models import Review


class ReviewFilter(filters.FilterSet):
    """Query parameters of the review list.

    Both filters are declared explicitly because the query parameter names carry
    an ``_id`` suffix that the model fields do not have.
    """

    business_user_id = filters.NumberFilter(field_name="business_user_id")
    reviewer_id = filters.NumberFilter(field_name="reviewer_id")

    class Meta:
        """Bind the two declared filters to the review model."""

        model = Review
        fields = ("business_user_id", "reviewer_id")
