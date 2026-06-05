from django.urls import path
from .views import ReviewCreateView, ReviewPendingListView, ReviewDetailView

urlpatterns = [
    path("", ReviewCreateView.as_view(), name="review-create"),
    # Admin only: Queue for unapproved reviews
    path("pending/", ReviewPendingListView.as_view(), name="review-pending"),
    # User: Update/Delete their own review
    # Admin: Approve a review (by updating is_approved)
    path("<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
]
