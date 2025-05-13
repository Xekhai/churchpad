from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Plan, Subscription

class SubscriptionAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test plan
        self.plan = Plan.objects.create(
            name='Test Plan',
            description='Test Description',
            price=9.99,
            stripe_price_id='price_test123'
        )
        
    @patch('subscriptions.views.stripe.Customer.create')
    @patch('subscriptions.views.stripe.Subscription.create')
    @patch('subscriptions.views.send_welcome_sms.delay')
    def test_subscribe_endpoint(self, mock_send_sms, mock_stripe_sub, mock_stripe_customer):
        # Mock Stripe responses
        mock_stripe_customer.return_value = MagicMock(id='cus_test123')
        mock_stripe_sub.return_value = MagicMock(id='sub_test123')
        
        # Test data
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'plan_id': self.plan.id
        }
        
        # Send request
        response = self.client.post(reverse('subscribe'), data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        
        # Check if customer was created with a source
        mock_stripe_customer.assert_called_once()
        call_kwargs = mock_stripe_customer.call_args[1]
        self.assertEqual(call_kwargs['email'], 'test@example.com')
        self.assertEqual(call_kwargs['name'], 'Test User')
        self.assertEqual(call_kwargs['phone'], '+1234567890')
        self.assertEqual(call_kwargs['source'], 'tok_visa')
        
        # Check if SMS was sent
        mock_send_sms.assert_called_once_with('Test User', '+1234567890')
        
    @patch('subscriptions.views.stripe.Subscription.delete')
    def test_unsubscribe_endpoint(self, mock_stripe_delete):
        # Create a test subscription
        subscription = Subscription.objects.create(
            name='Test User',
            email='test@example.com',
            phone_number='+1234567890',
            plan=self.plan,
            stripe_customer_id='cus_test123',
            stripe_subscription_id='sub_test123',
            active=True
        )
        
        # Send request
        response = self.client.delete(reverse('unsubscribe', args=[subscription.id]))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Refresh subscription from database
        subscription.refresh_from_db()
        self.assertFalse(subscription.active)
        
        # Check if Stripe was called
        mock_stripe_delete.assert_called_once_with('sub_test123')
        
    def test_subscriptions_list_endpoint(self):
        # Create some test subscriptions
        Subscription.objects.create(
            name='User 1',
            email='user1@example.com',
            phone_number='+1111111111',
            plan=self.plan,
            stripe_customer_id='cus_1',
            stripe_subscription_id='sub_1',
            active=True
        )
        
        Subscription.objects.create(
            name='User 2',
            email='user2@example.com',
            phone_number='+2222222222',
            plan=self.plan,
            stripe_customer_id='cus_2',
            stripe_subscription_id='sub_2',
            active=True
        )
        
        # Inactive subscription, should not be returned
        Subscription.objects.create(
            name='User 3',
            email='user3@example.com',
            phone_number='+3333333333',
            plan=self.plan,
            stripe_customer_id='cus_3',
            stripe_subscription_id='sub_3',
            active=False
        )
        
        # Send request
        response = self.client.get(reverse('subscriptions'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only the active subscriptions
