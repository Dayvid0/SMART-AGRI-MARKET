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
        limit_choices_to={'user_type': 'farmer'},
        help_text="Farmer who will fulfill the order"
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
        help_text="Product being ordered"
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
##```

### **Code Explanation:**

##Order Model:
##- `buyer`: Who is buying (consumer/business)
##- `farmer`: Who is selling
##- `order_number`: Unique ID like "ORD-20250208-001"
##- `status`: Track order progress
##- `total_amount`: Total cost

##**OrderItem Model:**
##- Links to parent Order
##- Stores product, quantity, price
##- `save()` method auto-calculates subtotal

##**Key Relationship:**
##```
##Order (1) -----> (Many) OrderItem
##One order can have multiple products##