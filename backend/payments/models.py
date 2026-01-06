from django.db import models
from orders.models import Order
from django.conf import settings
from products.models import Product


class Transaction(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="transactions"
    )
    reference_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="ID of transaction object (Checkout, Session, Order or whatever name it has) in Stripe/PayPal",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    # Store the raw response from the gateway for debugging
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.reference_id} - {self.status}"


class StockReservation(models.Model):
    """
    Temporary inventory hold for an order / Stripe Checkout Session.

    Design:
    - Reserve at "Proceed to checkout"
    - Release on session expiration/cancel or TTL expiry
    - Consume on successful payment (then decrement Product.stock_quantity)
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CONSUMED = "consumed", "Consumed"  # payment succeeded, applied to stock
        RELEASED = "released", "Released"  # expired/cancelled/abandoned

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="stock_reservations",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_reservations",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_reservations",
    )

    quantity = models.PositiveIntegerField()

    # One Stripe session typically corresponds to MANY reservation rows (one per product/order item).
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe Checkout Session ID (cs_...) used to correlate webhooks. "
        "Can be null until the session is created.",
    )

    status = models.CharField(
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        sid = (self.stripe_session_id or "")[:10]
        sid_display = f"{sid}..." if sid else "no-session"
        return f"{self.quantity}× {self.product_id} for Order {self.order_id} ({self.status}, {sid_display})"
