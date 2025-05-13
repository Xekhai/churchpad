from django.core.management.base import BaseCommand
from subscriptions.models import Plan
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

class Command(BaseCommand):
    help = 'Creates sample plans in the database and Stripe'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Basic',
                'description': 'Access to live streaming',
                'price': 9.99,
                'stripe_name': 'Basic Subscription'
            },
            {
                'name': 'Premium',
                'description': 'Access to live streaming and recordings',
                'price': 19.99,
                'stripe_name': 'Premium Subscription'
            },
            {
                'name': 'Family',
                'description': 'Access for up to 5 family members',
                'price': 29.99,
                'stripe_name': 'Family Subscription'
            }
        ]

        for plan_data in plans:
            # Create price in Stripe
            stripe_price = stripe.Price.create(
                unit_amount=int(plan_data['price'] * 100),  # Convert to cents
                currency='usd',
                recurring={'interval': 'month'},
                product_data={
                    'name': plan_data['stripe_name'],
                }
            )

            # Create plan in database
            Plan.objects.create(
                name=plan_data['name'],
                description=plan_data['description'],
                price=plan_data['price'],
                stripe_price_id=stripe_price.id
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created plan: {plan_data['name']}"))

