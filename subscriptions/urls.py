from django.urls import path
from .views import SubscribeAPIView, SubscriptionsListAPIView, UnsubscribeAPIView, stripe_webhook, PlansListAPIView

urlpatterns = [
    path('subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    path('subscriptions/', SubscriptionsListAPIView.as_view(), name='subscriptions'),
    path('unsubscribe/<int:id>/', UnsubscribeAPIView.as_view(), name='unsubscribe'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('plans/', PlansListAPIView.as_view(), name='plans'),
]   