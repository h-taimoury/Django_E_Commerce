from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.shortcuts import get_object_or_404
from orders.models import Order
from .models import Transaction
from .services import PaymentService
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import TransactionListSerializer, TransactionDetailSerializer


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status == "paid":
            return Response(
                {"error": "This order has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            checkout_url = PaymentService.create_checkout_session(order)
            return Response({"checkout_url": checkout_url}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            # This catches issues like invalid API keys, rate limits, or bad parameters
            return Response(
                {"error": f"Payment Gateway Error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception:
            # This catches things like database errors or unexpected Python bugs
            return Response(
                {"error": "An internal server error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")
    event = None
    try:
        # 1. Verify that the request actually came from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)  # Invalid payload
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)  # Invalid signature

    # 2. Handle the specific event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Call our service to fulfill the order
        # This updates the Transaction and the Order status
        order_key = session.get("client_reference_id")
        print(f"this is the order_key from session: {order_key}")
        success = PaymentService.fulfill_order(session)

        if not success:
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Always return a 200 OK to Stripe so they stop retrying
    return HttpResponse(status=status.HTTP_200_OK)


class TransactionListView(generics.ListAPIView):
    """View for Admins to list ALL transactions"""

    queryset = Transaction.objects.all().order_by("-created_at")
    serializer_class = TransactionListSerializer
    # Only users with is_staff=True can access this
    permission_classes = [permissions.IsAdminUser]


class TransactionDetailView(generics.RetrieveAPIView):
    """View for Admins to see full details of any transaction"""

    queryset = Transaction.objects.all()
    serializer_class = TransactionDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    # lookup_field = "id"
