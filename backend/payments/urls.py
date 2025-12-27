from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    stripe_webhook,
    TransactionListView,
    TransactionDetailView,
)

urlpatterns = [
    # User-facing endpoints
    path(
        "create-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
    # Admin-only endpoints
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/<int:id>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
]
