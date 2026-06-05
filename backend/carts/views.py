from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    CartItemWriteSerializer,
)
from orders.models import Order


# View to see the cart details
class CartDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


# View to add items to the cart
class CartItemAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemWriteSerializer

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        # Check if item already exists, if yes, increase quantity
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += quantity
            # Ensure quantity doesn't exceed stock
            if cart_item.quantity > product.quantity_available:
                cart_item.quantity = product.quantity_available
            cart_item.save()


# 3️⃣ View to update or delete a cart item
class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemWriteSerializer
    lookup_field = "pk"

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)


# 4️⃣ View to clear the cart
class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_200_OK)


# 5️⃣ View to initiate checkout
class CartCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        if not cart.items.exists():
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user has an unfinished order
        if Order.objects.filter(user=request.user, status="pending").exists():
            return Response(
                {"detail": "You already have an unfinished order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create an order
        order = Order.objects.create(user=request.user)
        for item in cart.items.all():
            order.items.create(
                product=item.product, quantity=item.quantity, price=item.product.price
            )

        # Optionally, clear the cart after checkout initiation
        cart.items.all().delete()

        from orders.serializers import OrderSerializer  # Assuming you have one

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
