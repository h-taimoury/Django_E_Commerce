import stripe
from django.conf import settings
from .models import Transaction
from orders.models import Order

# Initialize stripe with your secret key from settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY
# Using the following two lines we can check our account id related to the secret and publishable keys stored as env variables. Then we can compare it with the account id we see in stripe dashboard.
# acct = stripe.Account.retrieve()
# print("Stripe account id:", acct["id"])


class PaymentService:
    @staticmethod
    def create_checkout_session(order: Order):
        """
        Step 1: Create a session on the Payment Gateway's server.
        This generates a URL where the user will enter their card details.
        """
        # We use the order_key to identify this session in webhooks later
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order #{order.id}",
                        },
                        "unit_amount": int(order.total_paid * 100),  # Stripe uses cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL
            + "?session_id={CHECKOUT_SESSION_ID}",
            # cancel_url=settings.PAYMENT_CANCEL_URL,
            client_reference_id=order.order_key,  # Link Stripe session to our Order
        )
        # print("This is the Stripe session:", session)

        # Create an initial 'pending' transaction in our DB
        Transaction.objects.create(
            order=order,
            reference_id=session.id,
            amount=order.total_paid,
            status="pending",
        )

        return session.url

    @staticmethod
    def fulfill_order(session):
        """
        Step 2: This is called by the Webhook once payment is confirmed.
        It updates both the Transaction and the Order status.
        """
        order_key = session.get("client_reference_id")
        reference_id = session.get("id")

        try:
            order = Order.objects.get(order_key=order_key)

            # Update Transaction record
            transaction = Transaction.objects.get(reference_id=reference_id)
            transaction.status = "completed"
            transaction.raw_response = session  # Store full response for debugging
            transaction.save()

            # Update Order record in orders app
            order.status = "paid"
            order.save()

            return True
        except Exception as e:
            # Log failure
            print("this error happens in fulfill_order:", e)
            return False
