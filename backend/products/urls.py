from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()

# Register the ViewSets with the router
# Explicitly set the basename. This is mandatory for ProductViewSet which uses get_queryset() instead of a static queryset.
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

# The router generates all the URLs (list, detail, etc.)
urlpatterns = router.urls
