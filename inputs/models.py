from django.db import models
from accounts.models import User

class InputCategory(models.Model):
    """
    Categories for agricultural inputs
    """
    CATEGORY_TYPES = (
        ('seeds', 'Seeds'),
        ('fertilizers', 'Fertilizers'),
        ('pesticides', 'Pesticides'),
        ('herbicides', 'Herbicides'),
        ('tools', 'Tools & Equipment'),
        ('irrigation', 'Irrigation Equipment'),
    )
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='input_categories/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Input Category"
        verbose_name_plural = "Input Categories"


class AgriculturalInput(models.Model):
    """
    Agricultural inputs (seeds, fertilizers, pesticides, tools)
    """
    supplier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'input_supplier'},
        related_name='inputs'
    )
    category = models.ForeignKey(InputCategory, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.IntegerField()
    unit = models.CharField(max_length=50, help_text="e.g., kg, liters, pieces")
    
    # Product details
    manufacturer = models.CharField(max_length=200, blank=True)
    usage_instructions = models.TextField(blank=True)
    safety_warnings = models.TextField(blank=True)
    
    # Images
    image = models.ImageField(upload_to='inputs/')
    image2 = models.ImageField(upload_to='inputs/', blank=True, null=True)
    
    # Group buy feature
    min_group_order = models.IntegerField(
        default=1,
        help_text="Minimum quantity for group purchase discount"
    )
    group_discount_percentage = models.IntegerField(
        default=0,
        help_text="Discount % for group orders"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[('available', 'Available'), ('out_of_stock', 'Out of Stock')],
        default='available'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.supplier.username}"
    
    class Meta:
        verbose_name = "Agricultural Input"
        verbose_name_plural = "Agricultural Inputs"
        ordering = ['-created_at']


class GroupBuyPool(models.Model):
    """
    Group buying pools for bulk discounts on inputs
    """
    input_item = models.ForeignKey(AgriculturalInput, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_pools')
    
    target_quantity = models.IntegerField(help_text="Target quantity to unlock discount")
    current_quantity = models.IntegerField(default=0)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open for Joining'),
            ('closed', 'Target Reached'),
            ('completed', 'Order Placed'),
            ('cancelled', 'Cancelled')
        ],
        default='open'
    )
    
    deadline = models.DateTimeField(help_text="Deadline to reach target")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Group Buy: {self.input_item.name} ({self.current_quantity}/{self.target_quantity})"
    
    class Meta:
        verbose_name = "Group Buy Pool"
        verbose_name_plural = "Group Buy Pools"


class GroupBuyParticipant(models.Model):
    """
    Farmers participating in group buy
    """
    pool = models.ForeignKey(GroupBuyPool, on_delete=models.CASCADE, related_name='participants')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.farmer.username} - {self.quantity} units"
    
    class Meta:
        verbose_name = "Group Buy Participant"
        verbose_name_plural = "Group Buy Participants"
        unique_together = ['pool', 'farmer']