from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User, FarmerProfile, InputSupplierProfile, TransporterProfile, VerificationRequest
from notifications.models import Notification


class CustomUserAdmin(UserAdmin):
    """Custom admin configuration for the User model."""
    model = User

    list_display = [
        'username', 'email', 'user_type', 'district',
        'is_verified', 'is_staff', 'is_active',
    ]
    list_filter = ['user_type', 'is_verified', 'is_staff', 'is_active', 'district']
    search_fields = ['username', 'email', 'phone', 'location']

    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {
            'fields': (
                'user_type', 'phone', 'whatsapp_number',
                'location', 'address', 'district', 'specialization',
                'profile_picture', 'is_verified', 'first_login',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Info', {
            'fields': ('user_type', 'phone', 'whatsapp_number', 'location', 'district')
        }),
    )


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    """Admin panel for reviewing farmer/supplier verification requests."""
    list_display = ['user', 'user_type_display', 'status', 'submitted_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'user__user_type']
    search_fields = ['user__username', 'user__email', 'business_reg_number']
    readonly_fields = ['submitted_at', 'reviewed_at', 'reviewed_by']
    actions = ['approve_verifications', 'reject_verifications']

    def user_type_display(self, obj):
        return obj.user.get_user_type_display()
    user_type_display.short_description = 'User Type'

    @admin.action(description='✅ Approve selected verification requests')
    def approve_verifications(self, request, queryset):
        approved_count = 0
        for vr in queryset.filter(status='pending'):
            vr.status = 'approved'
            vr.reviewed_by = request.user
            vr.reviewed_at = timezone.now()
            vr.save()

            # Mark user as verified
            vr.user.is_verified = True
            vr.user.save(update_fields=['is_verified'])

            # Send in-app notification
            Notification.objects.create(
                user=vr.user,
                notification_type='system',
                title='Account Verified!',
                message='Congratulations! Your identity has been verified. You now appear with a Verified badge on the platform.',
                link='/accounts/dashboard/',
            )
            approved_count += 1

        self.message_user(request, f'{approved_count} verification(s) approved successfully.')

    @admin.action(description='❌ Reject selected verification requests')
    def reject_verifications(self, request, queryset):
        rejected_count = 0
        for vr in queryset.filter(status='pending'):
            vr.status = 'rejected'
            vr.reviewed_by = request.user
            vr.reviewed_at = timezone.now()
            vr.rejection_reason = 'Documents were unclear or insufficient. Please resubmit with clearer images.'
            vr.save()

            # Ensure is_verified is False
            vr.user.is_verified = False
            vr.user.save(update_fields=['is_verified'])

            # Notify user
            Notification.objects.create(
                user=vr.user,
                notification_type='system',
                title='Verification Request Update',
                message=f'Your verification request was not approved: {vr.rejection_reason}',
                link='/accounts/verification/submit/',
            )
            rejected_count += 1

        self.message_user(request, f'{rejected_count} verification(s) rejected.')


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'farm_name', 'farm_size', 'specialization', 'rating_average', 'total_sales']
    search_fields = ['user__username', 'farm_name']
    list_filter = ['specialization']


@admin.register(InputSupplierProfile)
class InputSupplierProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'specialization', 'rating_average']
    search_fields = ['user__username', 'company_name', 'business_license']


@admin.register(TransporterProfile)
class TransporterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_type', 'vehicle_registration', 'capacity_kg', 'rating_average', 'total_deliveries']
    list_filter = ['vehicle_type']
    search_fields = ['user__username', 'vehicle_registration']


# Register User with custom admin
admin.site.register(User, CustomUserAdmin)
