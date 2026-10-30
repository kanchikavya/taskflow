"""
Django admin configuration for custom User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extends Django's standard UserAdmin to include custom TaskFlow fields.
    """

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'is_active',
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # Add custom role field to the edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('TaskFlow Role', {'fields': ('role',)}),
    )

    # Add custom role field to the creation form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('TaskFlow Role', {'fields': ('role',)}),
    )
