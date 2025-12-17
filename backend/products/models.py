from django.db import models


# ----------------------------------------------------------------------------
# CORE EAV MODELS: START
# ----------------------------------------------------------------------------

# Define the data types that an Attribute can store.
# This prevents storing integers in a text field, for instance.
ATTRIBUTE_DATA_TYPES = (
    ("text", "Text (String)"),
    ("integer", "Integer (Number)"),
    ("decimal", "decimal (Decimal Number)"),
    ("boolean", "Boolean"),
    ("choice", "Choice (Select from Options)"),
)


class Attribute(models.Model):
    """
    Defines the product specification itself (e.g., 'RAM', 'Material', 'Color').
    This model represents the 'Attribute' in the EAV pattern.
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Used for filtering and API keys."
    )
    data_type = models.CharField(
        max_length=10,
        choices=ATTRIBUTE_DATA_TYPES,
        default="text",
        verbose_name="Data Type",
    )
    categories = models.ManyToManyField(
        "Category",
        related_name="attributes",
        blank=True,
        help_text="The categories this attribute is relevant for.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Product Attribute"
        verbose_name_plural = "Product Attributes"

    def __str__(self):
        return f"{self.name} ({self.data_type})"


class Option(models.Model):
    """
    Defines the valid choices for a 'choice' type Attribute.
    """

    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="options"
    )
    value = models.CharField(max_length=255)

    class Meta:
        # Ensures that the same option value cannot be used twice for the same attribute.
        unique_together = ("attribute", "value")
        ordering = ["value"]
        verbose_name = "Attribute Option"
        verbose_name_plural = "Attribute Options"

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Value(models.Model):
    """
    The central model linking a Product to an Attribute and holding the data.
    This model represents the 'Value' in the EAV pattern.
    """

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="values"
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.PROTECT, related_name="values"
    )

    # Fields to store the value based on the Attribute's data_type
    # We use separate fields for integrity and easier indexing/querying.
    value_text = models.TextField(blank=True, null=True)
    value_integer = models.IntegerField(blank=True, null=True)
    value_decimal = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    value_boolean = models.BooleanField(blank=True, null=True)

    # For 'choice' attributes, we link to a fixed option model for integrity
    value_option = models.ForeignKey(
        Option,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="values",
        help_text="Used when the attribute is a 'choice' type.",
    )

    class Meta:
        # A product can only have one value for any given attribute.
        unique_together = ("product", "attribute")
        verbose_name = "Product Attribute Value"
        verbose_name_plural = "Product Attribute Values"

    def __str__(self):
        # A utility method to fetch the correct value based on data type
        return f"{self.product.name} - {self.attribute.name}: {self.get_value()}"

    # A custom helper method
    def get_value(self):
        """Returns the actual value stored in the correct field."""
        data_type = self.attribute.data_type
        if data_type == "text":
            return self.value_text
        elif data_type == "integer":
            return self.value_integer
        elif data_type == "decimal":
            return self.value_decimal
        elif data_type == "boolean":
            return self.value_boolean
        elif data_type == "choice" and self.value_option:
            return self.value_option.value
        return None


# ----------------------------------------------------------------------------
# CORE EAV MODELS: END
# ----------------------------------------------------------------------------


class Category(models.Model):
    """
    Model for product categories (e.g., Electronics, Clothing, Books).
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model for individual products.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    main_image = models.ImageField(
        upload_to="product_images/main/",
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField("Category", related_name="products")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    Represents an auxiliary (gallery) image associated with a specific product.
    """

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product_images/gallery/")

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return f"{self.product.name} Gallery Image ({self.order})"
