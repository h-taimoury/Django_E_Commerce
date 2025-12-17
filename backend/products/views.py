from rest_framework import viewsets
from rest_framework.generics import (
    ListCreateAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)

# from rest_framework.filters import SearchFilter, OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Attribute, Option, Value
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
    AttributeListSerializer,
    AttributeDetailSerializer,
    AttributeWriteSerializer,
    OptionSerializer,
    ValueWriteSerializer,
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
            # Optimization for detail view
            return queryset.prefetch_related(
                "categories", "images", "values__attribute", "values__value_option"
            )

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


class AttributeViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Attributes (Product Specifications).
    Permissions: Read-only for all users, Admin-only for CUD.
    """

    queryset = Attribute.objects.all().prefetch_related("categories")
    permission_classes = [IsAdminOrReadOnly]

    # Optionally add filtering/searching if needed for the admin UI
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['name', 'slug']
    # ordering_fields = ['name']
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AttributeWriteSerializer
        if self.action == "retrieve":
            return AttributeDetailSerializer
        return AttributeListSerializer  # default for 'list'


class OptionListCreateAPIView(ListCreateAPIView):
    """
    Handles GET (list all options) and POST (create a new option).
    Read access for all, Write access for Admin only.
    """

    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [IsAdminOrReadOnly]


class ValueCreateAPIView(CreateAPIView):
    """
    Handles POST requests for creating a new Value instance at /api/values/.
    """

    queryset = Value.objects.all()
    serializer_class = ValueWriteSerializer
    permission_classes = [IsAdminOrReadOnly]


class ValueUpdateDestroyAPIView(UpdateAPIView, DestroyAPIView):
    """
    Handles PUT, PATCH, and DELETE requests for a specific Value instance
    at /api/values/{id}/.
    """

    queryset = Value.objects.all()
    serializer_class = ValueWriteSerializer
    permission_classes = [IsAdminOrReadOnly]
