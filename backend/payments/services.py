import stripe
from datetime import timedelta

from django.conf import settings
from django.db import transaction

# from django.db.models import Sum
from django.utils import timezone

from .models import Transaction, StockReservation
from orders.models import Order
from products.models import Product

# Initialize stripe with your secret key from settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY


class OutOfStockError(Exception):
    """Raised when one or more products do not have enough available quantity."""

    pass


class PaymentService:
    @staticmethod
    def _check_stock_and_reserve(order, user, expires_at):
        """
        Check stock and Reserve for each OrderItem in an order by:
        - first checking that sufficient quantity is available for each product
        - decrementing Product.quantity_available
        - creating StockReservation rows (ACTIVE)

        Must be called inside transaction.atomic().
        """

        items = order.items.all()
        if not items:
            raise ValueError("Order has no items")

        # Lock all involved products to prevent overselling under concurrency
        # You may ask why we didn't use the item.product to access the product in each order item. The reason is we needed to lock them all
        product_ids = [item.product_id for item in items]
        products_by_id = (
            Product.objects.select_for_update().filter(id__in=product_ids).in_bulk()
        )

        # 1) Decrement quantity_available (this is the "hold")
        for item in items:
            product = products_by_id[item.product_id]
            if product.quantity_available < item.quantity:
                raise OutOfStockError(
                    f"Not enough stock for product_id={product.id}. "
                    f"Available={product.quantity_available}, requested={item.quantity}"
                )
            product.quantity_available -= item.quantity
            product.save(update_fields=["quantity_available"])

        # 2) Create reservation rows as audit trail + release/consume tracking
        StockReservation.objects.bulk_create(
            [
                StockReservation(
                    order=order,
                    product=products_by_id[item.product_id],
                    user=user,
                    quantity=item.quantity,
                    expires_at=expires_at,
                    status=StockReservation.Status.ACTIVE,
                )
                for item in items
            ]
        )

    @staticmethod
    def create_checkout_session(order: Order, user):
        """
        Step 1: Called when user clicks 'Proceed to checkout'.
        - Reserve stock (decrement Product.quantity_available + create StockReservation rows)
        - Create Stripe Checkout Session (expires in 24h)
        - Store stripe_session_id in StockReservation rows
        - Create initial 'pending' Transaction
        """
        expires_at_dt = timezone.now() + timedelta(
            hours=24
        )  # timezone-aware datetime (Python/Django)

        expires_at_ts = int(
            expires_at_dt.timestamp()
        )  # Stripe expects a Unix timestamp (int seconds)

        with transaction.atomic():
            # Prevent duplicate reservations / sessions for the same order
            existing_session_id = (
                StockReservation.objects.filter(
                    order=order,
                    status=StockReservation.Status.ACTIVE,
                    expires_at__gt=timezone.now(),
                    stripe_session_id__isnull=False,
                )
                .values_list("stripe_session_id", flat=True)
                .first()
            )
            if existing_session_id:
                # Reuse existing session URL (Stripe allows retrieve)
                existing_session = stripe.checkout.Session.retrieve(existing_session_id)
                return existing_session.url

            # Reserve stock first (atomic with session creation)
            PaymentService._check_stock_and_reserve(
                order=order,
                user=user,
                expires_at=expires_at_dt,
            )

            # Create Stripe line items from order items
            line_items = []
            for item in order.items.select_related("product").all():
                line_items.append(
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {"name": item.product.name},
                            "unit_amount": int(item.price * 100),  # cents
                        },
                        "quantity": item.quantity,
                    }
                )

            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=settings.PAYMENT_SUCCESS_URL
                + "?session_id={CHECKOUT_SESSION_ID}",
                # cancel_url=settings.PAYMENT_CANCEL_URL,  # optional
                client_reference_id=order.order_key,
                expires_at=expires_at_ts,  # 30 min–24h, default 24h; you requested 24h
            )

            # Attach session.id to reservations created above
            StockReservation.objects.filter(
                order=order,
                status=StockReservation.Status.ACTIVE,
                expires_at=expires_at_dt,
                stripe_session_id__isnull=True,
            ).update(stripe_session_id=session.id)

            # Create initial 'pending' transaction in our DB
            Transaction.objects.create(
                order=order,
                reference_id=session.id,
                amount=order.total_paid,
                status="pending",
            )

            return session.url

    @staticmethod
    def release_reservations_for_session(session_id: str) -> bool:
        """
        Release ACTIVE reservations for an expired/cancelled Stripe session:
        - increment Product.quantity_available back
        - mark reservations as RELEASED
        """
        with transaction.atomic():
            reservations = list(
                StockReservation.objects.select_for_update().filter(
                    stripe_session_id=session_id,
                    status=StockReservation.Status.ACTIVE,
                )
            )
            if not reservations:
                return False

            product_ids = [r.product_id for r in reservations]
            products_by_id = (
                Product.objects.select_for_update().filter(id__in=product_ids).in_bulk()
            )

            for r in reservations:
                p = products_by_id[r.product_id]
                p.quantity_available += r.quantity
                p.save(update_fields=["quantity_available"])

            StockReservation.objects.filter(id__in=[r.id for r in reservations]).update(
                status=StockReservation.Status.RELEASED
            )

            return True

    @staticmethod
    def fulfill_order(session):
        """
        Step 2: Called by webhook when payment is confirmed.

        With reservations:
        - if payment succeeded, decrement Product.quantity_on_hand (physical stock)
        - mark StockReservation rows as CONSUMED
        - mark Transaction as completed and Order as paid

        IMPORTANT: do NOT decrement Product.quantity_available here, because it was already
        decremented when the reservation was created at checkout start.
        """
        order_key = session.get("client_reference_id")
        reference_id = session.get("id")

        # Basic safety check for Checkout
        if session.get("payment_status") != "paid":
            return False

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_key=order_key)

                # Idempotency guard (minimal)
                if order.status == "paid":
                    return True

                # Lock ACTIVE reservations for this order + session
                reservations = list(
                    StockReservation.objects.select_for_update().filter(
                        order=order,
                        stripe_session_id=reference_id,
                        status=StockReservation.Status.ACTIVE,
                    )
                )
                if not reservations:
                    # Could already be consumed/released or a mismatch; treat as failure for now
                    return False

                # Lock products and decrement physical stock (quantity_on_hand)
                product_ids = [r.product_id for r in reservations]
                products_by_id = (
                    Product.objects.select_for_update()
                    .filter(id__in=product_ids)
                    .in_bulk()
                )

                for r in reservations:
                    p = products_by_id[r.product_id]
                    if p.quantity_on_hand < r.quantity:
                        return False
                    p.quantity_on_hand -= r.quantity
                    p.save(update_fields=["quantity_on_hand"])

                # Mark reservations consumed
                StockReservation.objects.filter(
                    id__in=[r.id for r in reservations]
                ).update(status=StockReservation.Status.CONSUMED)

                # Update Transaction record
                txn = Transaction.objects.select_for_update().get(
                    reference_id=reference_id
                )
                if txn.status == "completed":
                    return True

                txn.status = "completed"
                txn.raw_response = session
                txn.save(update_fields=["status", "raw_response"])

                # Update Order record in orders app
                order.status = "paid"
                order.save(update_fields=["status"])

            return True

        except (Order.DoesNotExist, Transaction.DoesNotExist) as e:
            print("this error happens in fulfill_order:", e)
            return False
        except Exception as e:
            print("unexpected error in fulfill_order:", e)
            return False
