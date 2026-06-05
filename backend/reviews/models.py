from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from products.models import Product

User = settings.AUTH_USER_MODEL


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )

    # Stars: 1 to 5. Standard for e-commerce.
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField(max_length=1000)

    # Moderation logic
    is_approved = models.BooleanField(default=False)

    # Timestamps for "Sort by Newest"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Crucial: prevents a user from reviewing the same product twice
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating} Stars)"
