from django.db import models
from orders.models import Order


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
        return f"Transaction {self.transaction_id} - {self.status}"
