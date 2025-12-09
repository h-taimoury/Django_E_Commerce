from rest_framework import viewsets

# from rest_framework.filters import SearchFilter, OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
)
from .permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Product Categories.
    Permissions: Read-only for all users, Admin-only for CUD.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Products.
    Permissions: Read-only for all users, Admin-only for CUD.
    Includes filtering and searching.
    """

    permission_classes = [IsAdminOrReadOnly]

    # # Filters and Search
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["category", "price", "is_active"]
    # search_fields = ["name", "description"]
    # ordering_fields = ["price", "name", "created_at"]

    # ------------------
    # Custom Queryset Logic
    # ------------------
    # Handles complex logic: public vs. admin filtering + database optimization.
    def get_queryset(self):
        # 1. Base Queryset Filtering (Admin vs. Public)
        if self.request.user.is_staff:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(is_active=True)

        if self.action == "retrieve":
            # Optimization for detail view (includes comments)
            return queryset.prefetch_related("categories", "images")

        # Default minimal queryset for write operations (create, update, destroy)
        return queryset

    # ------------------
    # Custom Serializer Logic
    # ------------------
    # Handles selection of Read vs. Write serializers.
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer  # default for 'list'
