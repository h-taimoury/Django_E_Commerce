from rest_framework import serializers
from .models import Review
from orders.models import Order


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["product", "rating", "comment"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs["product"]

        # 1. Check if the user has a "delivered" order for this product
        has_purchased = Order.objects.filter(
            user=user,
            items__product=product,
            status="delivered",
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                "You can only review products that have been delivered to you."
            )

        # 2. Prevent duplicate reviews (Safety check)
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("You have already reviewed this product.")

        return attrs


class ReviewDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user_email",
            "product_name",
            "rating",
            "comment",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")

        # Check if 'is_approved' is being sent in the request
        if "is_approved" in attrs:
            # If the user is not an admin, raise a PermissionError (403 or 400)
            if request and not request.user.is_staff:
                raise serializers.ValidationError(
                    {
                        "is_approved": "Only staff members can modify the approval status."
                    }
                )

        return attrs
