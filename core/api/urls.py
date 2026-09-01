"""URL route for the base info endpoint.

Included under the ``api/`` prefix in ``core.urls``, which yields
``/api/base-info/``.
"""

from django.urls import path

from .views import BaseInfoView

urlpatterns = [
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
