from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User Model
class User(AbstractUser):
    """
    Custom user model that extends Django's default User.
    AbstractUser gives us: username, email, password, first_name, last_name
    We're adding: user_type, phone, location, address
    """
    
    # Define user types as choices
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('business', 'Business'),
    )
    
    # New fields we're adding
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPES,
        help_text="Type of user account"
    )
    phone = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Phone number with country code"
    )
    location = models.CharField(
        max_length=100,
        help_text="City or district (e.g., Kampala, Wakiso)"
    )
    address = models.TextField(
        blank=True,
        help_text="Detailed address"
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """
        This method defines how the object appears in admin panel
        """
        return f"{self.username} ({self.user_type})"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


# Farmer Profile (Additional info for farmers only)
class FarmerProfile(models.Model):
    """
    Extended profile for farmers only.
    OneToOneField means: one User can have only one FarmerProfile
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  # If user is deleted, delete this profile too
        related_name='farmer_profile'
    )
    farm_name = models.CharField(
        max_length=200,
        help_text="Name of the farm"
    )
    farm_size = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Farm size in acres"
    )
    specialization = models.CharField(
        max_length=200,
        help_text="Main crops/products (e.g., Matooke, Coffee)"
    )
    rating_average = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        help_text="Average rating from reviews"
    )
    total_sales = models.IntegerField(
        default=0,
        help_text="Total number of successful orders"
    )
    
    def __str__(self):
        return f"{self.farm_name} - {self.user.username}"
    
    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"