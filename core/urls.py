"""Root URL configuration.

Every app contributes its own ``urls`` module under the shared ``api/`` prefix,
so the paths inside those modules are written without it. The order of the
includes does not matter here because no two apps claim the same path.

Contents:
  * admin/ -- Django admin.
  * api/   -- authentication, profiles, offers, orders, reviews, base info.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.auth.urls")),
    path("api/", include("accounts.profile.urls")),
    path("api/", include("offers.api.urls")),
    path("api/", include("orders.api.urls")),
    path("api/", include("reviews.api.urls")),
    path("api/", include("core.api.urls")),
]
