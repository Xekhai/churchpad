from celery import shared_task
from django.conf import settings
from twilio.rest import Client

@shared_task
def send_welcome_sms(name, phone_number):
    """
    Send a welcome SMS to newly subscribed users using Twilio
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=f"Hi {name}, thanks for subscribing to our livestream service on ChurchPad!",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    
    return message.sid