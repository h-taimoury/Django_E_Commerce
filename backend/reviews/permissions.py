from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admins full access
        if request.user.is_staff:
            return True
        # Allow users to edit/delete only their own reviews
        return obj.user == request.user
