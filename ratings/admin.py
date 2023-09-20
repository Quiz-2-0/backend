from django.contrib import admin

from .models import Achivement, Rating, UserAchivement, UserLevel


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    """Административный класс для уровня пользователя."""

    list_display = (
        "level",
        "to_level_up",
    )


@admin.register(Achivement)
class AchivementAdmin(admin.ModelAdmin):
    """Административный класс для достижений."""

    list_display = ("name",)


@admin.register(UserAchivement)
class UserAchivementAdmin(admin.ModelAdmin):
    """Административный класс для достижений пользователя."""

    list_display = ("user", "achivement")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Административный класс для рейтинга пользователя."""

    list_display = ("user", "user_level", "user_rating")
