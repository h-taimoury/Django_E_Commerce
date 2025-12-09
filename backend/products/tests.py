from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

# We use the APIClient for making requests to DRF views
from rest_framework.test import APIClient
from rest_framework import status

from products.models import Category, Product, ProductImage

# Get the custom user model dynamically
User = get_user_model()


# --- URL Helper Functions ---


# Router URL names: 'category-list', 'category-detail', 'product-list', 'product-detail'
def category_list_url():
    """Generates the URL for the Category List endpoint."""
    # Matches router.register(r"categories", CategoryViewSet) -> 'category-list'
    return reverse("category-list")


def category_detail_url(pk):
    """Generates the URL for a specific Category Detail endpoint."""
    # Matches router.register(r"categories", CategoryViewSet) -> 'category-detail'
    return reverse("category-detail", kwargs={"pk": pk})


def product_list_url():
    """Generates the URL for the Product List endpoint."""
    # Matches router.register(r"products", ProductViewSet) -> 'product-list'
    return reverse("product-list")


def product_detail_url(pk):
    """Generates the URL for a specific Product Detail endpoint."""
    # Matches router.register(r"products", ProductViewSet) -> 'product-detail'
    return reverse("product-detail", kwargs={"pk": pk})


# --- Helper Functions for Test Setup ---


def create_user(**params):
    """Create and return a new regular user."""
    # Provide defaults consistent with your User model
    defaults = {
        "email": "regular@example.com",
        "password": "RegularPassword123",
        "first_name": "Jane",
        "last_name": "Doe",
    }
    defaults.update(params)
    return User.objects.create_user(**defaults)


def create_superuser(**params):
    """Create and return a new admin user."""
    # Provide defaults consistent with your User model
    defaults = {
        "email": "admin@example.com",
        "password": "AdminPassword123",
        "first_name": "System",
        "last_name": "Admin",
    }
    defaults.update(params)
    return User.objects.create_superuser(**defaults)


# --- Base Test Case Setup ---


class BaseProductTest(TestCase):
    """Base setup for all product-related tests."""

    def setUp(self):
        # Initialize an unauthenticated client
        self.client = APIClient()

        # Create user roles
        self.regular_user = create_user(email="user@test.com")
        self.admin_user = create_superuser(email="admin@test.com")

        # Initialize authenticated clients
        self.regular_client = APIClient()
        self.regular_client.force_authenticate(user=self.regular_user)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        # Create base test data
        self.category1 = Category.objects.create(name="A Books", slug="a-books")
        self.category2 = Category.objects.create(
            name="C Electronics", slug="c-electronics"
        )

        # Create an active product (publicly visible)
        self.active_product = Product.objects.create(
            name="Active Phone", slug="active-phone", price="500.00", is_active=True
        )
        self.active_product.categories.add(self.category2)

        # Create an inactive product (admin-only visible)
        self.inactive_product = Product.objects.create(
            name="Inactive Monitor",
            slug="inactive-monitor",
            price="200.00",
            is_active=False,
        )
        self.inactive_product.categories.add(self.category1)

        # Create an image for nested serializer testing
        ProductImage.objects.create(
            product=self.active_product, image="dummy/path/img1.jpg", order=1
        )


# --- Test Classes ---


class CategoryAPITests(BaseProductTest):
    """Tests the Category ViewSet permissions and basic CRUD."""

    def test_list_categories_public_allowed(self):
        """Test GET /categories/ is allowed for unauthenticated users."""
        res = self.client.get(category_list_url())

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check sorting by name (A Books then C Electronics)
        self.assertEqual(res.data[0]["name"], self.category1.name)
        self.assertEqual(len(res.data), 2)

    def test_create_category_unauthenticated_forbidden(self):
        """Test POST request is forbidden for unauthenticated users."""
        payload = {"name": "Test Category", "slug": "test-category"}
        res = self.client.post(category_list_url(), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_category_regular_user_forbidden(self):
        """Test POST request is forbidden for authenticated non-staff users."""
        payload = {"name": "Test Category", "slug": "test-category"}
        res = self.regular_client.post(category_list_url(), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_category_admin_success(self):
        """Test POST request is allowed and successful for admin user."""
        payload = {"name": "New Category", "slug": "new-category"}
        res = self.admin_client.post(category_list_url(), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(res.data["name"], payload["name"])

    def test_update_category_admin_success(self):
        """Test PATCH /categories/:id/ allows admin to update."""
        url = category_detail_url(self.category1.id)
        updated_name = "New Book Category"
        res = self.admin_client.patch(url, {"name": updated_name})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, updated_name)

    def test_delete_category_admin_success(self):
        """Test DELETE /categories/:id/ allows admin to delete."""
        url = category_detail_url(self.category1.id)
        res = self.admin_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category1.id).exists())


class ProductAPITests(BaseProductTest):
    """Tests the Product ViewSet permissions, queryset filtering, and serializers."""

    # --- Public/Read Tests (is_active filtering) ---

    def test_list_products_public_only_shows_active(self):
        """Test public users only see products where is_active=True."""
        res = self.client.get(product_list_url())

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], self.active_product.name)

    def test_retrieve_inactive_product_public_forbidden(self):
        """Test public users cannot view inactive products (should return 404)."""
        url = product_detail_url(self.inactive_product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_active_product_check_detail_serializer_fields(self):
        """Test public users retrieve product with full DetailSerializer fields."""
        url = product_detail_url(self.active_product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check fields from ProductDetailSerializer (nested relationships)
        self.assertIn("description", res.data)
        self.assertIsInstance(res.data["categories"], list)
        self.assertIsInstance(res.data["images"], list)
        self.assertEqual(len(res.data["images"]), 1)

    # --- Regular User (Read/Write Permission Tests) ---

    def test_create_product_regular_user_forbidden(self):
        """Test POST request is forbidden for authenticated non-staff users (IsAdminOrReadOnly)."""
        payload = {
            "name": "Forbidden Item",
            "slug": "forbidden-item",
            "price": "1.00",
            "categories": [],
        }
        res = self.regular_client.post(product_list_url(), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_regular_user_forbidden(self):
        """Test PATCH request is forbidden for authenticated non-staff users."""
        url = product_detail_url(self.active_product.id)
        res = self.regular_client.patch(url, {"price": "1000.00"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # --- Admin User (CUD and QuerySet) Tests ---

    def test_list_products_admin_shows_all_active_and_inactive(self):
        """Test admin users see both active and inactive products (overridden queryset)."""
        res = self.admin_client.get(product_list_url())

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        names = {item["name"] for item in res.data}
        self.assertIn(self.active_product.name, names)
        self.assertIn(self.inactive_product.name, names)
        # Check ListSerializer fields
        self.assertIn("url", res.data[0])

    def test_create_product_admin_success_check_m2m_set(self):
        """Test POST request uses ProductWriteSerializer and successfully sets M2M categories."""
        payload = {
            "name": "Admin Created Product",
            "slug": "admin-product-new",  # Changed slug to ensure uniqueness
            "description": "A wonderful new item.",
            "price": "50.00",
            "stock_quantity": 5,
            "is_active": True,
            # M2M relationship is handled here using PKs
            "categories": [self.category1.id, self.category2.id],
        }
        res = self.admin_client.post(product_list_url(), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_product = Product.objects.get(slug=payload["slug"])

        # Verify M2M relationship was set in the database
        self.assertEqual(new_product.categories.count(), 2)

        # Verify response structure contains the necessary data fields
        # Note: Since the serializer is not marked write_only, it returns all input fields.
        self.assertIn("name", res.data)
        self.assertIn("description", res.data)
        self.assertIn("url", res.data)

    def test_update_product_admin_success_patch_m2m_update(self):
        """Test PATCH request updates scalar fields and overwrites M2M categories."""
        url = product_detail_url(self.active_product.id)
        updated_payload = {
            "price": "999.99",
            # Overwrite existing categories (was only cat2, now only cat1)
            "categories": [self.category1.id],
        }
        res = self.admin_client.patch(url, updated_payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.active_product.refresh_from_db()

        # Verify scalar field update
        self.assertEqual(str(self.active_product.price), "999.99")

        # Verify M2M update (should now only have category1)
        self.assertEqual(self.active_product.categories.count(), 1)
        self.assertTrue(
            self.active_product.categories.filter(id=self.category1.id).exists()
        )
        self.assertFalse(
            self.active_product.categories.filter(id=self.category2.id).exists()
        )

    def test_delete_product_admin_success(self):
        """Test DELETE /products/:id/ allows admin to delete."""
        url = product_detail_url(self.active_product.id)
        res = self.admin_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.active_product.id).exists())
