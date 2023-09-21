from django.apps import AppConfig


class UserConfig(AppConfig):
    """Настройка приложения User."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "user"
