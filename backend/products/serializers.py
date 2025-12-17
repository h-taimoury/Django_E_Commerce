from rest_framework import serializers
from .models import Category, Product, ProductImage, Attribute, Option, Value


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


# ----------------------------------------------------------------------------
# EAV Serializers: START
# ----------------------------------------------------------------------------
# --- 1. EAV Attribute Option Serializer (List & Create) ---


# I intentionally didn't separate list, detail and write serializers for Option model. First, because we don't need and have an API endpoint to get an option data in detail like /api/options/:id/. Second, when listing the options, the only extra field may be attribute field which using the following serializer will include the related attribute's id. I don't want to create a separate serializer just to exclude a single field.
class OptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Option model, used for both Read (List) and Write (Create) operations.
    """

    class Meta:
        model = Option
        fields = "__all__"


# ----------------------------------------------------------------------------
# --- 2. EAV Attribute Serializers ---
class AttributeListSerializer(serializers.ModelSerializer):
    """Minimal serializer for listing Attribute records."""

    class Meta:
        model = Attribute
        fields = ["id", "name"]


class AttributeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for a single Attribute record."""

    # Nested options
    options = OptionSerializer(many=True)

    # categories M2M field
    categories = CategorySerializer(many=True)

    class Meta:
        model = Attribute
        fields = [
            "id",
            "name",
            "slug",
            "data_type",
            "categories",
            "options",  #
        ]
        read_only_fields = fields


class AttributeWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Attribute records."""

    class Meta:
        model = Attribute
        fields = [
            "id",
            "name",
            "slug",
            "data_type",
            "categories",  # M2M (writeable list of IDs)
        ]


# --- 3. EAV Attribute Value Serializers ---
class ValueListSerializer(serializers.ModelSerializer):
    """
    Serializer to display a single product specification for the frontend.
    It reads the related Attribute's name and uses the custom get_value() method.
    """

    attribute_name = serializers.CharField(source="attribute.name", read_only=True)

    # CRUCIAL: Uses the custom get_value() helper method on the model
    value = serializers.SerializerMethodField()

    class Meta:
        model = Value
        fields = [
            "id",
            "attribute_name",
            "value",
        ]

    def get_value(self, obj):
        """
        Calls the custom helper method on the Value model to retrieve
        the data from the correct value field (text, integer, decimal, or option).
        """
        return obj.get_value()


class ValueWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating EAV Value records (Admin Write API).
    """

    class Meta:
        model = Value
        fields = "__all__"

    # Note that this validation method receives a Product object, not the product id which is received as http request body (request.data)
    def validate_product(self, product):
        """
        Enforces that the product link cannot be changed after the Value object is created (we want product field to be immutable).
        """
        # 1. Check if we are currently updating an existing instance
        if self.instance is not None:
            # 2. Check if the provided 'value' (the input product ID) is different
            #    from the existing product ID on the instance.
            if product.id != self.instance.product_id:
                raise serializers.ValidationError(
                    "The product link for an existing Value record cannot be changed."
                    "This field is immutable after creation."
                )

        # 3. If it's a creation (self.instance is None) or if the ID hasn't changed,
        #    return the value to allow the process to continue.
        return product

    def validate(self, data):
        """
        Runs the three core EAV validation checks.
        """

        storage_fields = [
            "value_text",
            "value_integer",
            "value_decimal",
            "value_boolean",
            "value_option",
        ]

        # Determine the instance's attribute (handles both POST and PUT/PATCH)
        attribute_id = data.get(
            "attribute", self.instance.attribute.id if self.instance else None
        )

        if not attribute_id:
            # Should be caught by Django's required check, but good to be defensive
            raise serializers.ValidationError(
                {"attribute": "Attribute ID must be provided."}
            )

        try:
            attribute = Attribute.objects.get(pk=attribute_id)
        except Attribute.DoesNotExist:
            raise serializers.ValidationError({"attribute": "Invalid attribute ID."})

        # --- 1. Exclusivity Check: Only one field can be set ---
        # Note: We check if the field exists AND is not None
        set_fields = [field for field in storage_fields if data.get(field) is not None]

        if len(set_fields) > 1:
            raise serializers.ValidationError(
                f"Only one value field can be set at a time. Received values for: {', '.join(set_fields)}."
            )

        if len(set_fields) == 0:
            # If the serializer has an instance, it means it's a update request, trying to update the attribute without providing a value for the new attribute.
            if self.instance is not None:
                raise serializers.ValidationError(
                    {
                        "detail": "To update the attribute, providing a value field (e.g., value_text, value_integer) for this new attribute is required"
                    }
                )
            else:
                # If this is a POST (creation), a value is mandatory!
                # We raise an error indicating NO value field was provided.
                raise serializers.ValidationError(
                    {
                        "detail": "A value field (e.g., value_text, value_integer) is required for creation."
                    }
                )

        # --- 2. Type Match Check: we want to check if the field which is supposed to be set, matches attribute.data_type ---

        # Map Attribute data_type to the model storage field name
        type_to_field_map = {
            "text": "value_text",
            "integer": "value_integer",
            "decimal": "value_decimal",
            "boolean": "value_boolean",
            "choice": "value_option",
        }

        set_field_name = set_fields[0]
        expected_field_name = type_to_field_map.get(attribute.data_type)

        if set_field_name != expected_field_name:
            raise serializers.ValidationError(
                {
                    set_field_name: f"Attribute '{attribute.name}' is type '{attribute.data_type}', "
                    f"but value was provided in '{set_field_name}'. Expected field: '{expected_field_name}'."
                }
            )

        # --- 3. Option Scoping Check (only for 'choice' type) ---
        if attribute.data_type == "choice":
            option_pk = data.get("value_option")

            if option_pk is None:
                raise serializers.ValidationError(
                    {"value_option": "Choice attributes require a valid option ID."}
                )

            if not Option.objects.filter(
                pk=option_pk, attribute_id=attribute.id
            ).exists():
                raise serializers.ValidationError(
                    {
                        "value_option": "Selected option does not belong to this attribute."
                    }
                )
        return data


# ----------------------------------------------------------------------------
# EAV Serializers: END
# ----------------------------------------------------------------------------


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage (now only auxiliary/gallery images).
    """

    class Meta:
        model = ProductImage
        fields = ["id", "image", "order"]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for the product listing page (minimal data transfer).
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "main_image", "url"]
        read_only_fields = fields

    def get_url(self, obj):
        """Generates the combined slug-ID URL for the product."""
        return f"/products/{obj.slug}-{obj.id}/"


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the product detail page (minimal data transfer).
    """

    # The following line works because the related_name set in ProductImage model to Product model matches the field name defined in this serializer
    images = ProductImageSerializer(many=True)  # Nested gallery images

    # The following line works because we have a categories field in Product model
    # READ: Use nested CategorySerializer for listing all categories on GET requests
    categories = CategorySerializer(many=True)
    # The 'attribute_values' field comes from the related_name in the AttributeValue model
    specifications = ValueListSerializer(
        source="values",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock_quantity",
            "is_active",
            "main_image",
            "categories",  # The READ field (list of nested category objects)
            "images",  # Nested gallery images (ProductImage model)
            "specifications",
        ]
        read_only_fields = fields


class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Serializer used for creating (POST) and updating (PUT/PATCH) a Product.
    It includes all fields an Admin user is expected to provide or modify.
    """

    url = serializers.SerializerMethodField()

    # WRITE: Use PrimaryKeyRelatedField (with many=True) to accept a list of PKs
    # This is used for POST/PUT/PATCH requests.
    # categories = serializers.PrimaryKeyRelatedField(
    #     queryset=Category.objects.all(),
    #     many=True,  # REQUIRED for Many-to-Many fields
    #     write_only=True,  # Excludes it from GET requests
    # )

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "price",
            "stock_quantity",
            "is_active",
            "main_image",
            "categories",
            "url",
        ]
        read_only_fields = ["url"]

    def get_url(self, obj):
        """Generates the combined slug-ID URL for the product."""
        return f"/products/{obj.slug}-{obj.id}/"
