"""Management command that seeds the database with test data for frontend testing."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Profile
from offers.models import Offer, OfferDetail
from orders.models import Order
from reviews.models import Review


class Command(BaseCommand):
    """Creates business users, customer users, offers, orders, and reviews."""

    help = "Seeds the database with test data (users, offers, orders, reviews)."

    def handle(self, *args, **options):
        """Run all seeding steps in order and report progress to the console."""
        business_users = self.create_business_users()
        customer_users = self.create_customer_users()
        offers = self.create_offers(business_users)
        self.create_orders(customer_users, offers)
        self.create_reviews(customer_users, business_users)

        self.stdout.write(self.style.SUCCESS("Test data created successfully."))

    def create_business_users(self):
        """Create 2 business users with profiles, return them as a list."""
        data = [
            {
                "username": "biz_anna",
                "email": "anna@business.de",
                "location": "Berlin",
                "tel": "030123456",
                "description": "Grafikdesign und Branding",
                "working_hours": "9-17",
            },
            {
                "username": "biz_tom",
                "email": "tom@business.de",
                "location": "Hamburg",
                "tel": "040123456",
                "description": "Webentwicklung für kleine Unternehmen",
                "working_hours": "10-18",
            },
        ]
        users = []
        for entry in data:
            user, created = User.objects.get_or_create(
                username=entry["username"], defaults={"email": entry["email"]}
            )
            if created:
                user.set_password("testpass123")
                user.save()
                Profile.objects.create(
                    user=user,
                    type="business",
                    location=entry["location"],
                    tel=entry["tel"],
                    description=entry["description"],
                    working_hours=entry["working_hours"],
                )
            users.append(user)
        return users

    def create_customer_users(self):
        """Create 2 customer users with profiles, return them as a list."""
        usernames = ["cust_lena", "cust_max"]
        users = []
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@example.de"}
            )
            if created:
                user.set_password("testpass123")
                user.save()
                Profile.objects.create(user=user, type="customer")
            users.append(user)
        return users

    def create_offers(self, business_users):
        """Create one offer with 3 details per business user, return the offers."""
        offers = []
        for business_user in business_users:
            offer = Offer.objects.create(
                user=business_user,
                title=f"Design-Paket von {business_user.username}",
                description="Professionelles Design für dein Unternehmen.",
            )
            tier_data = [
                ("basic", "Basic", 2, 5, 100.0, ["Logo Design"]),
                ("standard", "Standard", 5, 7, 200.0, ["Logo Design", "Visitenkarte"]),
                (
                    "premium",
                    "Premium",
                    10,
                    10,
                    500.0,
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
                OfferDetail.objects.create(
                    offer=offer,
                    title=title,
                    revisions=revisions,
                    delivery_time_in_days=delivery_time,
                    price=price,
                    features=features,
                    offer_type=offer_type,
                )
            offers.append(offer)
        return offers

    def create_orders(self, customer_users, offers):
        """Create one order per customer, based on the 'basic' detail of the first offer."""
        if not offers:
            return
        basic_detail = offers[0].details.get(offer_type="basic")
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
