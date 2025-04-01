from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()  # Ensure it uses your custom user model

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'reg_number', 'is_active', 'is_staff', 'is_applicant')
    search_fields = ('email', 'full_name', 'reg_number')
    list_filter = ('is_active', 'is_staff', 'is_applicant')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'full_name', 'reg_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_applicant', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'reg_number', 'password1', 'password2', 'is_active', 'is_staff', 'is_applicant'),
        }),
    )

admin.site.register(User, CustomUserAdmin)  # Use `User` from `get_user_model()`
