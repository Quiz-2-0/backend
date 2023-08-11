from django.contrib import admin
from .models import (
    UserLevel,
    Achivement,
    UserAchivement,
    Rating
)


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'to_level_up', )


@admin.register(Achivement)
class AchivementAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(UserAchivement)
class UserAchivementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achivement')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_level', 'user_rating')