from django.shortcuts import render
import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription, Plan
from .serializers import SubscriptionSerializer, PlanSerializer
from .tasks import send_welcome_sms

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import json
import logging

# Configure Stripe
stripe.api_key = settings.STRIPE_API_KEY

class SubscribeAPIView(APIView):
    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Get the plan
                plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
                
                # Create a Stripe customer
                customer = stripe.Customer.create(
                    email=serializer.validated_data['email'],
                    name=serializer.validated_data['name'],
                    phone=serializer.validated_data['phone_number'],
                    # Use a token directly - this is a test token that always works
                    source="tok_visa"  # This represents a Visa card
                )
                
                # Create a Stripe subscription
                stripe_subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{'price': plan.stripe_price_id}]
                    # No need to specify payment method as it's already set via source
                )
                
                # Save subscription to database
                subscription = Subscription.objects.create(
                    name=serializer.validated_data['name'],
                    email=serializer.validated_data['email'],
                    phone_number=serializer.validated_data['phone_number'],
                    plan=plan,
                    stripe_customer_id=customer.id,
                    stripe_subscription_id=stripe_subscription.id
                )
                
                # Send welcome SMS asynchronously
                send_welcome_sms.delay(
                    subscription.name,
                    subscription.phone_number
                )
                
                return Response(
                    SubscriptionSerializer(subscription).data,
                    status=status.HTTP_201_CREATED
                )
                
            except Plan.DoesNotExist:
                return Response(
                    {"error": "Invalid plan ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except stripe.error.StripeError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionsListAPIView(APIView):
    def get(self, request):
        subscriptions = Subscription.objects.filter(active=True)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

class UnsubscribeAPIView(APIView):
    def delete(self, request, id):
        try:
            subscription = Subscription.objects.get(id=id, active=True)
            
            # Cancel the subscription in Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            
            # Update the database record
            subscription.active = False
            subscription.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Subscription.DoesNotExist:
            return Response(
                {"error": "Subscription not found or already cancelled"},
                status=status.HTTP_404_NOT_FOUND
            )
        except stripe.error.StripeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PlansListAPIView(APIView):
    def get(self, request):
        plans = Plan.objects.all()
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)
    
@csrf_exempt
@require_POST
def stripe_webhook(request):
    logger = logging.getLogger('subscriptions.webhook')
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    # Process the event based on its type
    event_type = event['type']
    event_object = event['data']['object']
    
    if event_type == 'customer.subscription.deleted':
        subscription_id = event_object['id']
        # Update your database
        subscription = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
        if subscription:
            subscription.active = False
            subscription.save()
            logger.info(f"Subscription {subscription_id} marked as inactive in database")

        else:
            logger.warning(f"Subscription {subscription_id} not found in database")    
    # Add other event handlers here
    
    return HttpResponse(status=200)