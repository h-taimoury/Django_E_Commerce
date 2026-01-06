from rest_framework import serializers
from .models import Address, OrderItem, Order
from products.models import Product
from django.db import transaction


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "user",
            "city",
            "address_line_1",
            "address_line_2",
            "postal_code",
            "is_default",
        ]
        read_only_fields = ["id", "user"]


class OrderItemSerializer(serializers.ModelSerializer):
    # This is for displaying the order details
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "price", "quantity"]


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "order_key",
            "total_paid",
            "status",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    address = AddressSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "address",
            "recipient_name",
            "total_paid",
            "status",
            "items",
            "created_at",
        ]
        read_only_fields = fields


class OrderWriteSerializer(serializers.ModelSerializer):
    order_items = serializers.ListField(
        write_only=True,
        child=serializers.DictField(),
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "address",
            "recipient_name",
            "order_items",
            "total_paid",
            "status",
            "order_key",
        ]
        read_only_fields = ["id", "total_paid", "status", "order_key"]

    def create(self, validated_data):
        items_data = validated_data.pop("order_items")
        user = validated_data.pop("user")
        address = validated_data["address"]

        total_price = 0
        order_items_to_create = []

        for item in items_data:
            product_id = item.get("product")
            quantity = item.get("quantity")

            if not product_id or quantity is None:
                raise serializers.ValidationError(
                    {"order_items": "Each item must include 'product' and 'quantity'."}
                )

            if int(quantity) <= 0:
                raise serializers.ValidationError(
                    {"order_items": f"Quantity must be >= 1 for product {product_id}."}
                )

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    {"order_items": f"Product with ID {product_id} does not exist."}
                )

            # Soft check (UX). Real check happens at reservation time in payments.
            if product.quantity_available < quantity:
                raise serializers.ValidationError(
                    {
                        "order_items": f"Not enough stock for '{product.name}'. "
                        f"Available={product.quantity_available}, requested={quantity}."
                    }
                )

            current_price = product.price
            total_price += current_price * quantity
            order_items_to_create.append(
                {"product": product, "price": current_price, "quantity": quantity}
            )

        # Snapshot address
        validated_data["shipping_address_line1"] = address.address_line_1
        validated_data["shipping_city"] = address.city
        validated_data["shipping_postal_code"] = address.postal_code

        with transaction.atomic():
            order = Order.objects.create(
                user=user, total_paid=total_price, **validated_data
            )
            OrderItem.objects.bulk_create(
                [
                    OrderItem(order=order, **item_info)
                    for item_info in order_items_to_create
                ]
            )

        return order
