from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product
from .models import Address, Order

User = get_user_model()

# URL Constants
ADDRESS_LIST_CREATE_URL = reverse("address-list")
ORDER_LIST_CREATE_URL = reverse("order-list-create")


def address_detail_url(address_id):
    return reverse("address-detail", kwargs={"pk": address_id})


def order_detail_url(order_id):
    return reverse("order-detail", kwargs={"pk": order_id})


class OrderIntegrationTests(APITestCase):
    def setUp(self):
        # Create two users for isolation testing using email as the identifier
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            phone_number="1234567890",  # Added based on our discussion
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            first_name="Other",
            last_name="User",
        )

        # Create test product with specific stock
        self.product = Product.objects.create(
            name="Test Product", price=100.00, stock_quantity=10
        )

        self.client.force_authenticate(user=self.user)

    # --- ADDRESS TESTS ---

    def test_create_address_auto_assigns_user(self):
        """Test that address creation automatically links to the authenticated user."""
        data = {
            "city": "Tehran",
            "address_line_1": "Main St 123",
            "postal_code": "123456",
        }
        response = self.client.post(ADDRESS_LIST_CREATE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.get(id=response.data["id"]).user, self.user)

    def test_default_address_logic(self):
        """Test that only one address can be set to is_default=True."""
        addr1 = Address.objects.create(user=self.user, city="City A", is_default=True)

        data = {
            "city": "City B",
            "address_line_1": "St 2",
            "postal_code": "987",
            "is_default": True,
        }
        self.client.post(ADDRESS_LIST_CREATE_URL, data)

        addr1.refresh_from_db()
        self.assertFalse(addr1.is_default)

    # --- ORDER TESTS ---

    def test_create_order_success_with_snapshot(self):
        """Test order creation, stock reduction, and address snapshotting."""
        address = Address.objects.create(
            user=self.user, city="Tehran", address_line_1="Snap St", postal_code="000"
        )

        data = {
            "address": address.id,
            "recipient_name": "John Doe",
            "order_items": [{"product": self.product.id, "quantity": 2}],
        }

        response = self.client.post(ORDER_LIST_CREATE_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check stock reduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

        # Check address snapshotting
        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.shipping_city, "Tehran")
        self.assertEqual(order.total_paid, 200.00)

    def test_order_insufficient_stock(self):
        """Test that order fails if requested quantity exceeds stock_quantity."""
        address = Address.objects.create(user=self.user, city="Tehran")
        data = {
            "address": address.id,
            "recipient_name": "Fail",
            "order_items": [{"product": self.product.id, "quantity": 100}],
        }

        response = self.client.post(ORDER_LIST_CREATE_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("left in stock", str(response.data))

    def test_order_isolation_security(self):
        """Test that users cannot retrieve orders belonging to others."""
        addr = Address.objects.create(user=self.other_user, city="Other City")
        order = Order.objects.create(
            user=self.other_user, address=addr, total_paid=10, recipient_name="Other"
        )

        url = order_detail_url(order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_is_read_only(self):
        """Verify that orders cannot be updated after creation."""
        addr = Address.objects.create(user=self.user, city="Tehran")
        order = Order.objects.create(
            user=self.user, address=addr, total_paid=10, recipient_name="Me"
        )

        url = order_detail_url(order.id)
        response = self.client.patch(url, {"status": "paid"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
