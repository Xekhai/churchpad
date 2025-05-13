# ChurchPad Subscription and Notification System

A Django REST API for managing church livestream subscriptions, including Stripe payment processing and Twilio SMS notifications.

## Features

- **Subscription Management**: Create and cancel subscriptions
- **Payment Processing**: Integration with Stripe for handling payments
- **Notification System**: Asynchronous SMS notifications using Twilio and Celery
- **Unit Tests**: Complete test suite for the API endpoints
- **Webhook Support**: Stripe webhook endpoint for subscription events

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/churchpad.git
   cd churchpad
   ```

2. Set up a virtual environment:

   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:

   ```
   STRIPE_API_KEY=sk_test_yourtestkeyhere
   STRIPE_WEBHOOK_SECRET=whsec_yoursecrethere
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

5. Apply migrations:

   ```
   python manage.py migrate
   ```

6. Create sample plans:

   ```
   python manage.py create_sample_plans
   ```

7. Run the development server:

   ```
   python manage.py runserver
   ```

8. In a separate terminal, start Redis and Celery worker:
   ```
   redis-server
   celery -A churchpad worker -l info
   ```

## API Endpoints

### 1. Create Subscription

- **URL**: `/subscribe/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "plan_id": 1
  }
  ```
- **Response**: 201 Created with subscription details

### 2. List Active Subscriptions

- **URL**: `/subscriptions/`
- **Method**: `GET`
- **Response**: 200 OK with list of active subscriptions

### 3. Cancel Subscription

- **URL**: `/unsubscribe/<id>/`
- **Method**: `DELETE`
- **Response**: 204 No Content on successful cancellation

### 4. Stripe Webhook (Bonus)

- **URL**: `/webhook/stripe/`
- **Method**: `POST`
- **Headers**: `Stripe-Signature: <signature>`
- **Body**: Stripe event payload
- **Response**: 200 OK when processed successfully

## Testing

Run the test suite with the following command:

```
python manage.py test
```

## Postman Collection

A Postman collection is included for testing all endpoints. Import the `ChurchPad API.postman_collection.json` file into Postman.

## Notes

- This project uses a test Stripe key. In production, use a proper Stripe account.
- For production, disable Django's DEBUG mode and use a production-ready database like PostgreSQL.
- The Celery worker needs to be running to send SMS notifications.

# .env (should be included in .gitignore for a real project)

STRIPE_API_KEY=sk_test_yourtestkeyhere
STRIPE_WEBHOOK_SECRET=whsec_yoursecrethere
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
