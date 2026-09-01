"""Admin registrations for the orders app."""

from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Browse orders and filter them by status or package tier."""

    list_display = (
        "title",
        "customer_user",
        "business_user",
        "status",
        "price",
        "created_at",
    )
    list_filter = ("status", "offer_type")
    search_fields = (
        "title",
        "customer_user__username",
        "business_user__username",
    )
