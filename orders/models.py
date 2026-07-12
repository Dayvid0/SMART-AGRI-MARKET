from django.db import models
from accounts.models import User
from marketplace.models import Product

class Order(models.Model):
    """
    Main order model - represents a purchase request
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Who placed the order
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_placed',
        help_text="User who placed the order"
    )
    
    # Who receives the order
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_received',
        limit_choices_to={'user_type__in': ['farmer', 'input_supplier']},
        help_text="Farmer or Supplier who will fulfill the order"
    )
    
    # Order details
    order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique order identifier"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total order amount in UGX"
    )
    
    # Delivery information
    delivery_address = models.TextField(
        help_text="Where to deliver the order"
    )
    delivery_phone = models.CharField(
        max_length=15,
        help_text="Contact phone for delivery"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or instructions"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.buyer.username}"
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    Individual items in an order
    One order can have multiple items
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent order"
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product being ordered"
    )

    input_product = models.ForeignKey(
        'inputs.AgriculturalInput',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Agricultural Input being ordered"
    )
    
    quantity = models.IntegerField(
        help_text="Quantity ordered"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of order"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity × Unit Price"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} × {self.product.name}"
    
    def save(self, *args, **kwargs):
        """
        Calculate subtotal automatically before saving
        """
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class DeliveryRequest(models.Model):
    """
    Links an order to a transporter for last-mile delivery.
    Farmers request delivery; transporters accept and fulfill.
    """
    STATUS_CHOICES = [
        ('open', 'Open — Looking for Transporter'),
        ('assigned', 'Assigned to Transporter'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name='delivery_request',
        help_text="Order this delivery is for"
    )
    transporter = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'user_type': 'transporter'},
        related_name='assigned_deliveries',
        help_text="Assigned transporter (blank = open request)"
    )

    pickup_district = models.CharField(
        max_length=100, help_text="District where goods will be picked up"
    )
    delivery_district = models.CharField(
        max_length=100, help_text="District where goods will be delivered"
    )
    pickup_address = models.TextField(
        blank=True, help_text="Specific pickup location / landmark"
    )

    # Financial
    offered_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Transport fee offered in UGX"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='open', db_index=True
    )
    notes = models.TextField(blank=True, help_text="Special delivery instructions")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.order_number} [{self.get_status_display()}]"

    class Meta:
        verbose_name = "Delivery Request"
        verbose_name_plural = "Delivery Requests"
        ordering = ['-created_at']