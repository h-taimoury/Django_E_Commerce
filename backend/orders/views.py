from rest_framework import generics, viewsets, permissions
from .models import Address, Order
from .serializers import (
    AddressSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderWriteSerializer,
)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Todo: Watch our video about Generics and ViewSets to find out why the following queryset doesn't make a problem for creating the first Address. We should look for something like "When creating a new record, how a DRF ViewSet uses the queryset".
    def get_queryset(self):
        # Users can only see and manage their own addresses
        return Address.objects.filter(user=self.request.user)

    def handle_default_address(self, serializer):
        """
        Utility method to ensure only one address is default for a user.
        """
        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user=self.request.user, is_default=True).update(
                is_default=False
            )

    def perform_create(self, serializer):
        # Handle is_default logic before saving
        self.handle_default_address(serializer)
        # Save the address with the authenticated user
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Handle is_default logic before saving the update
        self.handle_default_address(serializer)
        serializer.save()


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Security: Users only see their own orders
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderWriteSerializer
        return OrderListSerializer

    def perform_create(self, serializer):
        # Add the user during the save process
        serializer.save(user=self.request.user)


class OrderRetrieveView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
