"""Article permissions."""

from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class IsAdminUserOrReadOnly(IsAdminUser):
    """From https://stackoverflow.com.

    slug title: django-rest-framework-permission-isadminorreadonly
    """

    def has_permission(self, request, view):
        """Permission method."""
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin
