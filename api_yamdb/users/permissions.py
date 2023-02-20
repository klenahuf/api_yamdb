from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Разрешение для пользователей с правами администратора."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser))
