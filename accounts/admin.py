from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FarmerProfile, InputSupplierProfile


class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the User model
    """
    model = User

    # Columns shown in admin list view
    list_display = [
        'username',
        'email',
        'user_type',
        'location',
        'is_verified',
        'is_staff',
    ]

    # Sidebar filters
    list_filter = [
        'user_type',
        'is_verified',
        'is_staff',
        'is_active',
    ]

    # Fields when editing a user
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'user_type',
                'phone',
                'whatsapp_number',
                'location',
                'address',
                'profile_picture',
                'is_verified',
            )
        }),
    )

    # Fields when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': (
                'user_type',
                'phone',
                'whatsapp_number',
                'location',
            )
        }),
    )


# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(FarmerProfile)
admin.site.register(InputSupplierProfile)
