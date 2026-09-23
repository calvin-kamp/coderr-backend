"""Management command that seeds the database with test data for frontend testing."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Profile
from offers.models import Offer, OfferDetail
from orders.models import Order
from reviews.models import Review

User = get_user_model()


class Command(BaseCommand):
    """Creates business users, customer users, offers, orders, and reviews."""

    help = "Seeds the database with test data (users, offers, orders, reviews)."

    def handle(self, *args, **options):
        """Run all seeding steps in order and report progress to the console."""
        with transaction.atomic():
            business_users = self.create_business_users()
            customer_users = self.create_customer_users()
            offers = self.create_offers(business_users)
            self.create_orders(customer_users, offers)
            self.create_reviews(customer_users, business_users)

        self.stdout.write(self.style.SUCCESS("Test data created successfully."))

    def create_user(self, username, email, user_type, first_name, last_name):
        """Create or fetch one user together with its profile."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "type": user_type,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        if created:
            user.set_password("testpass123")
            user.save(update_fields=["password"])
        return user

    def create_business_users(self):
        """Create 2 business users with profiles, return them as a list."""
        data = [
            {
                "username": "biz_anna",
                "email": "anna@business.de",
                "first_name": "Anna",
                "last_name": "Brand",
                "location": "Berlin",
                "tel": "030123456",
                "description": "Grafikdesign und Branding",
                "working_hours": "9-17",
            },
            {
                "username": "biz_tom",
                "email": "tom@business.de",
                "first_name": "Tom",
                "last_name": "Weber",
                "location": "Hamburg",
                "tel": "040123456",
                "description": "Webentwicklung für kleine Unternehmen",
                "working_hours": "10-18",
            },
        ]
        users = []
        for entry in data:
            user = self.create_user(
                username=entry["username"],
                email=entry["email"],
                user_type=User.RoleChoices.BUSINESS,
                first_name=entry["first_name"],
                last_name=entry["last_name"],
            )
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    "location": entry["location"],
                    "tel": entry["tel"],
                    "description": entry["description"],
                    "working_hours": entry["working_hours"],
                },
            )
            users.append(user)
        return users

    def create_customer_users(self):
        """Create 2 customer users with profiles, return them as a list."""
        data = [
            {"username": "cust_lena", "first_name": "Lena", "last_name": "Vogt"},
            {"username": "cust_max", "first_name": "Max", "last_name": "Hoffmann"},
        ]
        users = []
        for entry in data:
            user = self.create_user(
                username=entry["username"],
                email=f"{entry['username']}@example.de",
                user_type=User.RoleChoices.CUSTOMER,
                first_name=entry["first_name"],
                last_name=entry["last_name"],
            )
            Profile.objects.get_or_create(user=user)
            users.append(user)
        return users

    def create_offers(self, business_users):
        """Create one offer with 3 details per business user, return the offers."""
        offers = []
        for business_user in business_users:
            offer, created = Offer.objects.get_or_create(
                user=business_user,
                title=f"Design-Paket von {business_user.username}",
                defaults={
                    "description": "Professionelles Design für dein Unternehmen.",
                },
            )
            tier_data = [
                (OfferDetail.OfferChoices.BASIC, "Basic", 2, 5, 100, ["Logo Design"]),
                (
                    OfferDetail.OfferChoices.STANDARD,
                    "Standard",
                    5,
                    7,
                    200,
                    ["Logo Design", "Visitenkarte"],
                ),
                (
                    OfferDetail.OfferChoices.PREMIUM,
                    "Premium",
                    10,
                    10,
                    500,
                    ["Logo Design", "Visitenkarte", "Flyer"],
                ),
            ]
            for (
                offer_type,
                title,
                revisions,
                delivery_time,
                price,
                features,
            ) in tier_data:
                OfferDetail.objects.get_or_create(
                    offer=offer,
                    offer_type=offer_type,
                    defaults={
                        "title": title,
                        "revisions": revisions,
                        "delivery_time_in_days": delivery_time,
                        "price": price,
                        "features": features,
                    },
                )
            offers.append(offer)
        return offers

    def create_orders(self, customer_users, offers):
        """Create one order per customer, based on the 'basic' detail of the first offer."""
        if not offers:
            return
        basic_detail = offers[0].details.get(offer_type=OfferDetail.OfferChoices.BASIC)
        for customer_user in customer_users:
            Order.objects.get_or_create(
                customer_user=customer_user,
                business_user=offers[0].user,
                defaults={
                    "title": basic_detail.title,
                    "revisions": basic_detail.revisions,
                    "delivery_time_in_days": basic_detail.delivery_time_in_days,
                    "price": basic_detail.price,
                    "features": basic_detail.features,
                    "offer_type": basic_detail.offer_type,
                },
            )

    def create_reviews(self, customer_users, business_users):
        """Create one review per customer for the first business user."""
        comments = [
            "Sehr professionell, gerne wieder!",
            "Schnelle Lieferung, gutes Ergebnis.",
        ]
        for customer_user, comment in zip(customer_users, comments):
            Review.objects.get_or_create(
                business_user=business_users[0],
                reviewer=customer_user,
                defaults={"rating": 5, "description": comment},
            )
