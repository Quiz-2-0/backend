from django.contrib import admin
from .models import (
    UserLevel,
    Achivment,
    UserAchvment,
    Rating
)


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'to_level_up', )


@admin.register(Achivment)
class AchivmentAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(UserAchvment)
class UserAchvmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'achivment')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_level', 'user_rating')