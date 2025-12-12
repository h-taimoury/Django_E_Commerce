from rest_framework import serializers
from .models import Category, Product, ProductImage, Attribute, Option, Value


# --- 1. EAV Attribute Option Serializer ---
class OptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Option model, used for displaying valid choices for an Attribute.
    """

    class Meta:
        model = Option
        fields = ["id", "value"]


# --- 2. EAV Attribute Value Serializer (Read) ---
class AttributeValueReadSerializer(serializers.ModelSerializer):
    """
    Serializer to display a single product specification for the frontend.
    It reads the related Attribute's name and uses the custom get_value() method.
    """

    # Nested field to display the Attribute's name and type
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)
    attribute_slug = serializers.CharField(source="attribute.slug", read_only=True)
    data_type = serializers.CharField(source="attribute.data_type", read_only=True)

    # CRUCIAL: Uses the custom get_value() helper method on the model
    value = serializers.SerializerMethodField()

    class Meta:
        model = Value
        fields = [
            "attribute_name",
            "attribute_slug",
            "data_type",
            "value",
        ]

    def get_value(self, obj):
        """
        Calls the custom helper method on the AttributeValue model to retrieve
        the data from the correct value field (text, integer, float, or option).
        """
        return obj.get_value()


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


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
    specifications = AttributeValueReadSerializer(
        source="attribute_values",  # Use the attribute_values queryset
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
