# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
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