from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FarmerProfile

# Customize how User appears in admin panel
class CustomUserAdmin(UserAdmin):
    """
    Customizes the admin interface for our User model
    """
    model = User
    
    # Fields to display in user list
    list_display = ['username', 'email', 'user_type', 'location', 'is_staff']
    
    # Filters in right sidebar
    list_filter = ['user_type', 'is_staff', 'is_active']
    
    # Add our custom fields to the user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'location', 'address', 'profile_picture')
        }),
    )
    
    # Fields for creating new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'location', 'address')
        }),
    )

# Register models with admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(FarmerProfile)