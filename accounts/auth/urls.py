"""URL routes for the authentication endpoints.

Included under the ``api/`` prefix in ``core.urls``, which yields
``/api/registration/`` and ``/api/login/``.
"""

from django.urls import path

from .views import LoginView, RegisterView

urlpatterns = [
    path("registration/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
