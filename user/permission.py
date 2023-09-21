from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """
    Класс разрешений.

    Позволяет только чтение для всех пользователей,
    но предоставляет полный доступ для администраторов.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение запроса.

        Если запрос является безопасным или пользователь является администратором,
        то доступ предоставляется.
        """
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверка доступа пользователя для выполнения запроса к конкретному объекту.

        Если запрос является безопасным или пользователь является администратором,
        то доступ предоставляется.
        """
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )
