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
        address = validated_data.get("address")

        with transaction.atomic():
            total_price = 0
            order_items_to_create = []

            for item in items_data:
                try:
                    product = Product.objects.select_for_update().get(
                        id=item["product"]
                    )
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            "product": f"Product with ID {item.get('product')} does not exist."
                        }
                    )

                quantity = item["quantity"]

                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        {product.name: f"Only {product.stock_quantity} left in stock."}
                    )

                product.stock_quantity -= quantity
                product.save()

                current_price = product.price
                total_price += current_price * quantity

                order_items_to_create.append(
                    {"product": product, "price": current_price, "quantity": quantity}
                )

            # Map snapshot fields from the address instance to validated_data
            # This "freezes" the address details at the moment of purchase
            validated_data["shipping_address_line1"] = address.address_line_1
            validated_data["shipping_city"] = address.city
            validated_data["shipping_postal_code"] = address.postal_code

            # 3. Create the Order with the snapshot data included in **validated_data
            order = Order.objects.create(
                user=user, total_paid=total_price, **validated_data
            )

            for item_info in order_items_to_create:
                OrderItem.objects.create(order=order, **item_info)

            return order
