from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewCreateSerializer, ReviewDetailSerializer
from .permissions import IsOwnerOrAdmin


class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the currently logged-in user
        # is_approved remains False by default as per your model
        serializer.save(user=self.request.user)


class ReviewPendingListView(generics.ListAPIView):
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Only return reviews that are NOT yet approved
        return Review.objects.filter(is_approved=False)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
