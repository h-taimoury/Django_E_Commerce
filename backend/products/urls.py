from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    AttributeViewSet,
    OptionListCreateAPIView,
    OptionDestroyAPIView,
    ValueCreateAPIView,
    ValueUpdateDestroyAPIView,
)

router = DefaultRouter()

# Register the ViewSets with the router
# Explicitly set the basename. This is mandatory for ProductViewSet which uses get_queryset() instead of a static queryset.
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"attributes", AttributeViewSet, basename="attribute")
# The router generates all the URLs (list, detail, etc.)
urlpatterns = router.urls
urlpatterns += [
    # EAV Options endpoint (List/Create)
    path("options/", OptionListCreateAPIView.as_view(), name="option-list-create"),
    path(
        "options/<int:pk>/",
        OptionDestroyAPIView.as_view(),
        name="option-detail",
    ),
]
urlpatterns += [
    # EAV Value Endpoints (CUD - Generic Views)
    path("values/", ValueCreateAPIView.as_view(), name="value-create"),
    path(
        "values/<int:pk>/",
        ValueUpdateDestroyAPIView.as_view(),
        name="value-detail",
    ),
]
