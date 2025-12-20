from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from products.models import Category, Product, Attribute, Option, Value


# Get the custom user model dynamically
User = get_user_model()

# --- URL Name Definitions ---
# These names should match the names defined in your urls.py for products app
LOGIN_URL = reverse("login")  # /api/users/login/ (Custom View)
CATEGORY_LIST_CREATE_URL = reverse("category-list")  # /api/categories/
PRODUCT_LIST_CREATE_URL = reverse("product-list")  # /api/products/
ATTRIBUTE_LIST_CREATE_URL = reverse("attribute-list")  # /api/attributes/
OPTION_LIST_CREATE_URL = reverse("option-list-create")  # /api/options/
VALUE_CREATE_URL = reverse("value-create")  # /api/values/


# Helper functions to generate URL for detail views (e.g., /api/products/1/)
def category_detail_url(category_id):
    return reverse("category-detail", kwargs={"pk": category_id})


def product_detail_url(product_id):
    return reverse("product-detail", kwargs={"pk": product_id})


def attribute_detail_url(attribute_id):
    return reverse("attribute-detail", kwargs={"pk": attribute_id})


def option_detail_url(option_id):
    return reverse("option-detail", kwargs={"pk": option_id})


def value_detail_url(value_id):
    return reverse("value-detail", kwargs={"pk": value_id})


User = get_user_model()


# class CategoryIntegrationTests(APITestCase):
#     def setUp(self):
#         # 1. Create admin and regular users
#         self.admin_user = User.objects.create_superuser(
#             email="admin@test.com", password="password123"
#         )
#         self.regular_user = User.objects.create_user(
#             email="user@test.com", password="password123"
#         )

#         # 2. Setup initial data
#         self.category = Category.objects.create(name="Electronics", slug="electronics")

#     # --- CREATE Tests ---
#     def test_admin_can_create_category(self):
#         self.client.force_authenticate(user=self.admin_user)
#         data = {"name": "Home Appliances", "slug": "home-appliances"}
#         response = self.client.post(CATEGORY_LIST_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_anonymous_cannot_create_category(self):
#         """Integration: Anonymous user should get 401."""
#         data = {"name": "Illegal", "slug": "illegal"}
#         response = self.client.post(CATEGORY_LIST_CREATE_URL, data)
#         # DRF returns 401 because no credentials were provided
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_regular_user_cannot_create_category(self):
#         """Integration: Authenticated non-staff user should get 403."""
#         self.client.force_authenticate(user=self.regular_user)
#         data = {"name": "Illegal", "slug": "illegal"}
#         response = self.client.post(CATEGORY_LIST_CREATE_URL, data)
#         # User is known but not allowed -> 403
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     # --- DELETE Tests ---
#     def test_anonymous_cannot_delete_category(self):
#         """Integration: Anonymous user should get 401."""
#         url = category_detail_url(self.category.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_regular_user_cannot_delete_category(self):
#         """Integration: Authenticated non-staff user should get 403."""
#         self.client.force_authenticate(user=self.regular_user)
#         url = category_detail_url(self.category.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_admin_can_delete_category(self):
#         self.client.force_authenticate(user=self.admin_user)
#         url = category_detail_url(self.category.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     # --- READ Tests ---
#     def test_public_can_list_categories(self):
#         response = self.client.get(CATEGORY_LIST_CREATE_URL)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)


# class AttributeIntegrationTests(APITestCase):
#     def setUp(self):
#         # 1. Create regular and admin users
#         self.admin_user = User.objects.create_superuser(
#             email="admin@test.com", password="password123"
#         )
#         self.regular_user = User.objects.create_user(
#             email="user@test.com", password="password123"
#         )

#         # 2. Setup Category
#         self.category = Category.objects.create(name="Tech", slug="tech")

#         # 3. Setup initial Attribute
#         self.attribute = Attribute.objects.create(
#             name="RAM", slug="ram", data_type="integer"
#         )
#         self.attribute.categories.add(self.category)

#     # --- CREATE Tests ---
#     def test_admin_can_create_attribute(self):
#         """Integration: Admin can POST with categories."""
#         self.client.force_authenticate(user=self.admin_user)
#         data = {
#             "name": "Color",
#             "slug": "color",
#             "data_type": "choice",
#             "categories": [self.category.id],
#         }
#         response = self.client.post(ATTRIBUTE_LIST_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_regular_user_cannot_create_attribute(self):
#         """Integration: Authenticated non-staff user gets 403."""
#         self.client.force_authenticate(user=self.regular_user)
#         data = {"name": "New", "slug": "new", "data_type": "text"}
#         response = self.client.post(ATTRIBUTE_LIST_CREATE_URL, data)

#         # Correctly identifies user but denies permission
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_anonymous_cannot_create_attribute(self):
#         """Integration: Unauthenticated user gets 401."""
#         response = self.client.post(ATTRIBUTE_LIST_CREATE_URL, {})
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # --- UPDATE Tests ---
#     def test_admin_can_update_attribute_categories(self):
#         """Integration: Admin can PATCH categories."""
#         self.client.force_authenticate(user=self.admin_user)
#         url = attribute_detail_url(self.attribute.id)

#         # Remove categories by sending empty list
#         response = self.client.patch(url, {"categories": []}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.attribute.refresh_from_db()
#         self.assertEqual(self.attribute.categories.count(), 0)

#     def test_regular_user_cannot_update_attribute(self):
#         """Integration: Authenticated non-staff user cannot PATCH."""
#         self.client.force_authenticate(user=self.regular_user)
#         url = attribute_detail_url(self.attribute.id)

#         response = self.client.patch(url, {"name": "Hacked"})
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         # Verify DB didn't change
#         self.attribute.refresh_from_db()
#         self.assertEqual(self.attribute.name, "RAM")

#     # --- DELETE Tests ---
#     def test_admin_can_delete_attribute(self):
#         self.client.force_authenticate(user=self.admin_user)
#         url = attribute_detail_url(self.attribute.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_regular_user_cannot_delete_attribute(self):
#         """Integration: Authenticated non-staff user cannot DELETE."""
#         self.client.force_authenticate(user=self.regular_user)
#         url = attribute_detail_url(self.attribute.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(Attribute.objects.count(), 1)

#     # --- READ Tests ---
#     def test_regular_user_can_read_attribute(self):
#         """Integration: Authenticated non-staff user CAN read (Safe Method)."""
#         self.client.force_authenticate(user=self.regular_user)
#         url = attribute_detail_url(self.attribute.id)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)


# class OptionIntegrationTests(APITestCase):
#     def setUp(self):
#         # 1. Create admin and regular users
#         self.admin_user = User.objects.create_superuser(
#             email="admin@test.com", password="password123"
#         )
#         self.regular_user = User.objects.create_user(
#             email="user@test.com", password="password123"
#         )

#         # 2. Requirement: An Option needs an Attribute
#         self.attribute = Attribute.objects.create(
#             name="Color", slug="color", data_type="choice"
#         )

#         # 3. Create an initial Option
#         self.option = Option.objects.create(attribute=self.attribute, value="Red")

#     # --- CREATE Tests ---
#     def test_admin_can_create_option(self):
#         """Integration: Admin can link a new option to an attribute."""
#         self.client.force_authenticate(user=self.admin_user)
#         data = {"attribute": self.attribute.id, "value": "Blue"}
#         response = self.client.post(OPTION_LIST_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Option.objects.count(), 2)

#     def test_regular_user_cannot_create_option(self):
#         """Integration: Non-staff user gets 403."""
#         self.client.force_authenticate(user=self.regular_user)
#         response = self.client.post(OPTION_LIST_CREATE_URL, {"value": "Green"})
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_unique_together_constraint_api(self):
#         """Integration: API should reject duplicate values for the same attribute."""
#         self.client.force_authenticate(user=self.admin_user)
#         # Attempt to create "Red" again for the same attribute
#         data = {"attribute": self.attribute.id, "value": "Red"}
#         response = self.client.post(OPTION_LIST_CREATE_URL, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn(
#             "non_field_errors", response.data
#         )  # unique_together usually raises this

#     # --- READ Tests ---
#     def test_public_can_list_options(self):
#         """Integration: Anyone can view the list of options."""
#         response = self.client.get(OPTION_LIST_CREATE_URL)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     # --- DELETE Tests ---
#     def test_admin_can_delete_unused_option(self):
#         """Integration: Admin can delete an option that isn't in use."""
#         self.client.force_authenticate(user=self.admin_user)
#         url = option_detail_url(self.option.id)
#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Option.objects.count(), 0)

#     def test_delete_protected_option_fails(self):
#         """
#         Integration: Test the ProtectedError handling in OptionDestroyAPIView.
#         Should return 400 if the option is currently used in a Product specification.
#         """
#         # 1. Create a product and a value that uses this option
#         product = Product.objects.create(name="Shirt", slug="shirt", price=10)
#         Value.objects.create(
#             product=product, attribute=self.attribute, value_option=self.option
#         )

#         self.client.force_authenticate(user=self.admin_user)
#         url = option_detail_url(self.option.id)
#         response = self.client.delete(url)

#         # 2. Verify custom response from the view's try-except ProtectedError block
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             response.data["detail"],
#             "Cannot delete this option because it is in use by one or more products.",
#         )

#     def test_regular_user_cannot_delete_option(self):
#         """Integration: Authenticated non-staff user gets 403."""
#         self.client.force_authenticate(user=self.regular_user)
#         url = option_detail_url(self.option.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class ValueIntegrationTests(APITestCase):
#     def setUp(self):
#         # 1. Create admin and regular users
#         self.admin_user = User.objects.create_superuser(
#             email="admin@test.com", password="password123"
#         )
#         self.regular_user = User.objects.create_user(
#             email="user@test.com", password="password123"
#         )

#         # 2. Setup Base Objects
#         self.product = Product.objects.create(name="Laptop", slug="laptop", price=1000)
#         self.product_two = Product.objects.create(name="Phone", slug="phone", price=500)

#         # 3. Attributes of different types
#         self.attr_int = Attribute.objects.create(
#             name="RAM", slug="ram", data_type="integer"
#         )
#         self.attr_text = Attribute.objects.create(
#             name="Color", slug="color", data_type="text"
#         )
#         self.attr_choice = Attribute.objects.create(
#             name="Material", slug="material", data_type="choice"
#         )

#         # 4. Option for choice attribute
#         self.option_metal = Option.objects.create(
#             attribute=self.attr_choice, value="Metal"
#         )
#         self.option_plastic = Option.objects.create(
#             attribute=self.attr_choice, value="Plastic"
#         )

#     # --- CREATE & EXCLUSIVITY VALIDATION ---
#     def test_admin_can_create_value_integer(self):
#         """Integration: Admin can create an integer value for an integer attribute."""
#         self.client.force_authenticate(user=self.admin_user)
#         data = {
#             "product": self.product.id,
#             "attribute": self.attr_int.id,
#             "value_integer": 16,
#         }
#         response = self.client.post(VALUE_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Value.objects.get(product=self.product).value_integer, 16)

#     def test_validation_exclusivity_fails(self):
#         """Integration: Serializer should fail if two value fields are provided."""
#         self.client.force_authenticate(user=self.admin_user)
#         data = {
#             "product": self.product.id,
#             "attribute": self.attr_int.id,
#             "value_integer": 16,
#             "value_text": "Wrong Field",
#         }
#         response = self.client.post(VALUE_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Only one value field can be set", str(response.data))

#     def test_validation_type_mismatch_fails(self):
#         """Integration: Fail if value_text is used for an integer attribute."""
#         self.client.force_authenticate(user=self.admin_user)
#         data = {
#             "product": self.product.id,
#             "attribute": self.attr_int.id,
#             "value_text": "Sixteen",
#         }
#         response = self.client.post(VALUE_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Expected field: 'value_integer'", str(response.data))

#     # --- CHOICE & SCOPING VALIDATION ---
#     def test_choice_scoping_validation(self):
#         """Integration: Cannot use an option belonging to a different attribute."""
#         other_attr = Attribute.objects.create(
#             name="Size", slug="size", data_type="choice"
#         )
#         wrong_option = Option.objects.create(attribute=other_attr, value="Large")

#         self.client.force_authenticate(user=self.admin_user)
#         data = {
#             "product": self.product.id,
#             "attribute": self.attr_choice.id,  # Material
#             "value_option": wrong_option.id,  # But using 'Size' option
#         }
#         response = self.client.post(VALUE_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             response.data["value_option"][0],
#             "Selected option does not belong to this attribute.",
#         )

#     # --- IMMUTABILITY & UPDATE ---
#     def test_product_field_is_immutable(self):
#         """Integration: validate_product should prevent changing the product link."""
#         # 1. Setup existing value
#         value = Value.objects.create(
#             product=self.product, attribute=self.attr_int, value_integer=8
#         )

#         self.client.force_authenticate(user=self.admin_user)
#         url = value_detail_url(value.id)

#         # 2. Attempt to move this value to a different product
#         data = {"product": self.product_two.id}
#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("immutable", str(response.data["product"][0]))

#     def test_admin_can_update_actual_value(self):
#         """Integration: Admin can update the value field of an existing record."""
#         value = Value.objects.create(
#             product=self.product, attribute=self.attr_int, value_integer=8
#         )
#         self.client.force_authenticate(user=self.admin_user)
#         url = value_detail_url(value.id)

#         response = self.client.patch(url, {"value_integer": 32})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         value.refresh_from_db()
#         self.assertEqual(value.value_integer, 32)

#     # --- PERMISSIONS ---
#     def test_regular_user_cannot_create_value(self):
#         self.client.force_authenticate(user=self.regular_user)
#         data = {
#             "product": self.product.id,
#             "attribute": self.attr_int.id,
#             "value_integer": 1,
#         }
#         response = self.client.post(VALUE_CREATE_URL, data)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_anonymous_cannot_delete_value(self):
#         value = Value.objects.create(
#             product=self.product, attribute=self.attr_int, value_integer=8
#         )
#         url = value_detail_url(value.id)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductIntegrationTests(APITestCase):
    def setUp(self):
        # 1. Setup admin and regular Users
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        self.public_user = User.objects.create_user(
            email="user@example.com", password="password123"
        )

        # 2. Setup Base Infrastructure
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.attr_ram = Attribute.objects.create(
            name="RAM", slug="ram", data_type="integer"
        )
        self.attr_color = Attribute.objects.create(
            name="Color", slug="color", data_type="choice"
        )
        self.option_red = Option.objects.create(attribute=self.attr_color, value="Red")

    # --- Full Workflow Test ---
    def test_full_product_specification_workflow(self):
        """
        Integration: Full journey from product creation to EAV attachment and public display.
        """
        self.client.force_authenticate(user=self.admin_user)

        # Step 1: Create a Product
        product_data = {
            "name": "Pro Laptop",
            "slug": "pro-laptop",
            "description": "High performance",
            "price": "1500.00",
            "categories": [self.category.id],
            "is_active": True,
        }
        product_res = self.client.post(
            reverse("product-list"), product_data, format="json"
        )
        self.assertEqual(product_res.status_code, status.HTTP_201_CREATED)
        product_id = product_res.data["id"]

        # Step 2: Attach an Integer Value (RAM)
        ram_data = {
            "product": product_id,
            "attribute": self.attr_ram.id,
            "value_integer": 16,
        }
        ram_res = self.client.post(reverse("value-create"), ram_data)
        self.assertEqual(ram_res.status_code, status.HTTP_201_CREATED)

        # Step 3: Attach a Choice Value (Color)
        color_data = {
            "product": product_id,
            "attribute": self.attr_color.id,
            "value_option": self.option_red.id,
        }
        color_res = self.client.post(reverse("value-create"), color_data)
        self.assertEqual(color_res.status_code, status.HTTP_201_CREATED)

        # Step 4: Verify Public Retrieval (Detail View)
        self.client.logout()
        detail_url = reverse("product-detail", kwargs={"pk": product_id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check nested specifications list
        specs = response.data["specifications"]
        self.assertEqual(len(specs), 2)

        # Verify custom get_value() logic and attribute naming is reflected
        spec_names = [s["attribute_name"] for s in specs]
        self.assertIn("RAM", spec_names)
        self.assertIn("Color", spec_names)

    # --- NEW: EAV Integrity Check ---
    def test_eav_integrity_api_rejection(self):
        """
        Integration: Verify that ValueWriteSerializer correctly rejects mismatched data types.
        """
        self.client.force_authenticate(user=self.admin_user)
        product = Product.objects.create(name="Test", slug="test", price=10)

        # Attempt to post string data to an integer attribute field
        invalid_data = {
            "product": product.id,
            "attribute": self.attr_ram.id,  # Integer type
            "value_text": "Invalid String Data",
        }
        response = self.client.post(reverse("value-create"), invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the serializer correctly identified the field mismatch
        self.assertIn("value_text", response.data)
        self.assertIn("Expected field: 'value_integer'", str(response.data))

    # --- NEW: Protected Option Deletion ---
    def test_protected_option_deletion_via_api(self):
        """
        Integration: Verify ProtectedError handling when an option is in use.
        """
        self.client.force_authenticate(user=self.admin_user)
        product = Product.objects.create(name="Test", slug="test", price=10)

        # Link the option to a product value
        Value.objects.create(
            product=product, attribute=self.attr_color, value_option=self.option_red
        )

        # Attempt to delete the option
        delete_url = reverse("option-detail", kwargs={"pk": self.option_red.id})
        res_delete = self.client.delete(delete_url)

        # Verify the custom error message from the OptionDestroyAPIView
        self.assertEqual(res_delete.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res_delete.data["detail"],
            "Cannot delete this option because it is in use by one or more products.",
        )

    # --- Permission Boundaries ---
    def test_permission_boundaries(self):
        """Integration: Test read-only for public and 403 for unauthorized writes."""
        # 1. Anonymous can list
        res_list = self.client.get(reverse("product-list"))
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)

        # 2. Regular user cannot create attributes
        self.client.force_authenticate(user=self.public_user)
        res_create = self.client.post(reverse("attribute-list"), {"name": "Size"})
        self.assertEqual(res_create.status_code, status.HTTP_403_FORBIDDEN)
