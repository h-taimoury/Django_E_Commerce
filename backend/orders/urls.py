from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, OrderListCreateView, OrderRetrieveView

router = DefaultRouter()
router.register(r"addresses", AddressViewSet, basename="address")

urlpatterns = [
    path("", include(router.urls)),
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderRetrieveView.as_view(), name="order-detail"),
]
