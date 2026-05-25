from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# Register your models here.

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = [
        'email',
        'username',
        'is_superuser',
    ]

admin.site.register(CustomUser,CustomUserAdmin)