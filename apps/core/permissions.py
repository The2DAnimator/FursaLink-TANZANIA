"""Reusable DRF permission classes implementing role-based access control."""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: only the owner may edit; everyone may read.

    The owning user is resolved from one of the common attribute names found on
    the platform's models.
    """

    owner_fields = ("owner", "user", "created_by", "seller", "posted_by")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        for field in self.owner_fields:
            owner = getattr(obj, field, None)
            if owner is not None:
                return owner == request.user
        return False


class IsAdmin(permissions.BasePermission):
    """Allow only super admins / staff."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_super_admin))


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_super_admin))


class HasRole(permissions.BasePermission):
    """Generic role gate. Set ``required_roles`` on the view.

    Example::

        class JobViewSet(viewsets.ModelViewSet):
            permission_classes = [HasRole]
            required_roles = {"business_owner", "seller"}
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        required = getattr(view, "required_roles", None)
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_super_admin or user.is_staff:
            return True
        if not required:
            return True
        return user.role in required
