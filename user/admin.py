from django.contrib import admin

from user.models import DefaultAvatar, Department, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Административный класс для модели User.

    Отображает email, имя и фамилию пользователя в списке пользователей.
    Настроен поиск пользователей по email и имени.
    """

    list_display = ("email", "firstName", "lastName")
    search_fields = ("email", "firstName")

    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель пользователя.

        Если пароль пользователя не был зашифрован,
        то сначала шифрует пароль, а затем сохраняет модель.
        """
        if not obj.password.startswith("pbkdf2_sha256"):
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Department.

    Отображает название отдела в списке отделов.
    Позволяет искать отделы по названию.
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(DefaultAvatar)
class DefaultAvatarAdmin(admin.ModelAdmin):
    """
    Административный класс для модели DefaultAvatar.

    Отображает аватар и описание в списке аватаров.
    """

    list_display = ("avatar", "description")
