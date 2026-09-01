"""Admin registrations for the accounts app.

``UserAdmin`` has to be subclassed rather than used as-is: the base class lists
the fields of Django's own user model, so the custom ``type`` field would be
missing from both the change form and the add form.

Contents:
  * UserAdmin    -- change and add forms for the custom user model.
  * ProfileAdmin -- read and edit profile data without going through the API.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Change and add forms for the custom user model.

    ``add_fieldsets`` is overridden as well because ``type`` is required, so it
    has to be part of the creation form and not only of the change form.
    """

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "type")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "type", "password1", "password2"),
            },
        ),
    )

    list_display = ("username", "email", "type", "is_staff")
    list_filter = ("type", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Browse profiles and find them by username or location."""

    list_display = ("user", "location", "tel", "created_at")
    search_fields = ("user__username", "location")
