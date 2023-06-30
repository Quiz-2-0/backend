from django.contrib import admin
from user.models import User, Department


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstName', 'lastName')
    search_fields = ('email', 'firstName')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
