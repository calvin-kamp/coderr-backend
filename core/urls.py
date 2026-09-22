"""Root URL configuration.

Every app contributes its own ``urls`` module under the shared ``api/`` prefix,
so the paths inside those modules are written without it. The order of the
includes does not matter here because no two apps claim the same path.

Contents:
  * admin/ -- Django admin.
  * api/   -- authentication, profiles, offers, orders, reviews, base info.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.auth.urls")),
    path("api/", include("accounts.profile.urls")),
    path("api/", include("offers.api.urls")),
    path("api/", include("orders.api.urls")),
    path("api/", include("reviews.api.urls")),
    path("api/", include("core.api.urls")),
]

# Uploaded files, served by Django itself (also with DEBUG=False).
urlpatterns += [
    re_path(
        rf"^{settings.MEDIA_URL.lstrip('/')}(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
