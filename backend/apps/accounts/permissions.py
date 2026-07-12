from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """Object-level: only the owning user may access/modify their own record."""

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(request.user and request.user.is_authenticated and obj == request.user)
