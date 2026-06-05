from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="cart-detail"),
    path("items/", views.CartItemAddView.as_view(), name="cart-item-add"),
    path(
        "items/<int:pk>/",
        views.CartItemUpdateDeleteView.as_view(),
        name="cart-item-manage",
    ),
    path("clear/", views.CartClearView.as_view(), name="cart-clear"),
    path("checkout/", views.CartCheckoutView.as_view(), name="cart-checkout"),
    path(
        "sync/", views.CartSyncView.as_view(), name="cart-sync"
    ),  # To sync the cart in user's local storage with the cart in the database when user logs in
]
