from django.contrib import admin
from .models import Plan, Subscription

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stripe_price_id')
    search_fields = ('name',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'plan', 'active', 'created_at')
    list_filter = ('active', 'plan')
    search_fields = ('name', 'email', 'phone_number')