from django.db import models
from django.conf import settings
from products.models import Product
import uuid

User = settings.AUTH_USER_MODEL


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    city = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.city}"


STATUS_CHOICES = (
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="orders"
    )
    # Snapshot fields to preserve history
    shipping_address_line1 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)

    recipient_name = models.CharField(
        max_length=150, help_text="The person who will receive the package"
    )
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    # Generated during the checkout process to sync with the payment gateway
    order_key = order_key = models.CharField(
        max_length=255,
        unique=True,
        default=uuid.uuid4,  # Note: pass the function, don't call it like uuid4()
        editable=False,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.PROTECT
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Item {self.id} for Order {self.order.id}"
