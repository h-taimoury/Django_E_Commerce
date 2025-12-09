from rest_framework import serializers
from .models import Category, Product, ProductImage


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


# products/serializers.py

# Assuming imports for Product, CategorySerializer, and ProductImageSerializer


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
