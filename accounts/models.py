# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .constants import UGANDA_DISTRICT_CHOICES, SPECIALIZATION_CHOICES

class User(AbstractUser):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('business', 'Business'),
        ('input_supplier', 'Input Supplier'),
        ('transporter', 'Transporter'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    district = models.CharField(
        max_length=100, 
        choices=UGANDA_DISTRICT_CHOICES, 
        blank=True
    )
    specialization = models.CharField(
        max_length=100, 
        choices=SPECIALIZATION_CHOICES, 
        blank=True
    )
    first_login = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Farm size in acres")
    specialization = models.CharField(max_length=200, choices=SPECIALIZATION_CHOICES)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_sales = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.farm_name} - {self.user.username}"

class InputSupplierProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    company_name = models.CharField(max_length=200)
    business_license = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=200, choices=SPECIALIZATION_CHOICES)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"


class TransporterProfile(models.Model):
    """
    Profile for transporter users — vehicle details and coverage area.
    """
    VEHICLE_TYPES = [
        ('motorcycle', 'Motorcycle / Boda-Boda'),
        ('pickup', 'Pickup Truck'),
        ('lorry', 'Lorry / Truck'),
        ('van', 'Van / Mini-Bus'),
        ('tractor', 'Tractor'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='transporter_profile'
    )
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    vehicle_registration = models.CharField(
        max_length=20, blank=True, help_text="Number plate e.g. UAA 123B"
    )
    capacity_kg = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Maximum load capacity in kg"
    )
    coverage_districts = models.TextField(
        help_text="Comma-separated districts covered e.g. Kampala,Wakiso,Mukono"
    )
    rating_average = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00
    )
    total_deliveries = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.get_vehicle_type_display()})"

    def get_districts_list(self):
        return [d.strip() for d in self.coverage_districts.split(',') if d.strip()]


class VerificationRequest(models.Model):
    """
    Verification requests submitted by farmers and suppliers.
    Admin approves → user.is_verified = True.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='verification_request'
    )
    # Identity documents
    national_id_image = models.ImageField(
        upload_to='verifications/ids/',
        blank=True, null=True,
        help_text="National ID or passport scan"
    )
    farm_or_business_photo = models.ImageField(
        upload_to='verifications/farms/',
        blank=True, null=True,
        help_text="Photo of farm, business premises, or vehicle"
    )
    business_reg_number = models.CharField(
        max_length=100, blank=True,
        help_text="Business registration number (if applicable)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional context from the applicant"
    )

    # Workflow
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (shown to user)"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verifications_reviewed'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_status_display()}"

    class Meta:
        verbose_name = "Verification Request"
        verbose_name_plural = "Verification Requests"
        ordering = ['-submitted_at']