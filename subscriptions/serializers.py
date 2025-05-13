from rest_framework import serializers
from .models import Subscription, Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'price']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'name', 'email', 'phone_number', 'plan', 'plan_id', 'active', 'created_at']
        read_only_fields = ['id', 'active', 'created_at']
    
    def validate_plan_id(self, value):
        try:
            Plan.objects.get(id=value)
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Invalid plan ID")
        return value