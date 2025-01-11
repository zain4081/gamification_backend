from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsPmOrAdmin(BasePermission):
    """
    CustomPagination.py permission to grant access only to users with 'owner' or 'admin' roles,
    or to superusers.
    """

    def has_permission(self, request, view):
        # Ensure the user is active
        if not request.user.is_active:
            raise PermissionDenied({"error": "Your Account Status is Inactive"})

        # Check if the user has the 'owner' or 'admin' role, or if they are a superuser
        if request.user.is_pm or request.user.is_admin:
            return True

        raise PermissionDenied({"error": "You do not have permission to perform this action."})

class IsUserOrAdmin(BasePermission):
    """
    CustomPagination.py permission to grant access only to users with 'gardener' or 'admin' roles,
    or to superusers.
    """

    def has_permission(self, request, view):
        # Ensure the user is active
        if not request.user.is_active:
            raise PermissionDenied({"error": "Your Account Status is Inactive"})

        # Check if the user has the 'owner' or 'admin' role, or if they are a superuser
        user_role = getattr(request.user, 'role', None)
        if not request.user.is_pm or request.user.is_admin:
            return True

        raise PermissionDenied({"error": "You do not have permission to perform this action."})

class IsAdmin(BasePermission):
    """
    CustomPagination.py permission to grant access only to users with 'admin' roles,
    or to superusers.
    """

    def has_permission(self, request, view):
        # Ensure the user is active
        if not request.user.is_active:
            raise PermissionDenied({"error": "Your Account Status is Inactive"})

        if request.user.is_admin:
            return True

        raise PermissionDenied({"error": "You do not have permission to perform this action."})

class IsSelf(BasePermission):
    """
    CustomPagination.py permission to grant access only to the user accessing their own resource,
    or to admin users.
    """

    def has_object_permission(self, request, view, obj):
        # Ensure the user is active
        if not request.user.is_active:
            raise PermissionDenied({"error": "Your Account Status is Inactive"})

        # Check if the user is accessing their own data or is an admin
        if obj == request.user:
            return True

        raise PermissionDenied({"error": "You do not have permission to access this resource."})
