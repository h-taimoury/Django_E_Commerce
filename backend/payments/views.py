from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.shortcuts import get_object_or_404
from orders.models import Order
from .models import Transaction
from .services import PaymentService, OutOfStockError
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import TransactionListSerializer, TransactionDetailSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


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
            checkout_url = PaymentService.create_checkout_session(
                order=order, user=request.user
            )
            return Response({"checkout_url": checkout_url}, status=status.HTTP_200_OK)

        except OutOfStockError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Payment Gateway Error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except Exception as e:
            print("This error happened:", e)
            return Response(
                {"error": "An internal server error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    event_type = event.get("type")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        success = PaymentService.fulfill_order(session)
        if not success:
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif event_type == "checkout.session.expired":
        # Release held stock if the checkout session expires
        PaymentService.release_reservations_for_session(session.get("id"))

    # Always return 200 so Stripe doesn't keep retrying on successful handling
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
