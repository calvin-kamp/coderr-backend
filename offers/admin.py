"""Admin registrations for the offers app.

Contents:
  * OfferAdmin       -- browse offers by title, description or owner.
  * OfferDetailAdmin -- browse the package tiers independently of their offer.
"""

from django.contrib import admin

from .models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Browse offers and find them by title, description or owner."""

    list_display = ("title", "user", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description", "user__username")


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Browse the package tiers independently of their offer."""

    list_display = ("offer", "offer_type", "price", "delivery_time_in_days")
    list_filter = ("offer_type",)
    search_fields = ("offer__title", "title")
