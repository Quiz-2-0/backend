from django.contrib import admin
from user.models import User, Department


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstName', 'lastName')
    search_fields = ('email', 'firstName')

    def save_model(self, request, obj, form, change):
        if not obj.password.startswith('pbkdf2_sha256'):
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
