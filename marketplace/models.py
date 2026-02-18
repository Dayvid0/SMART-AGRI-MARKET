from django.db import models
from accounts.models import User

# Product Category
class Category(models.Model):
    """
    Categories for organizing products (Vegetables, Fruits, Cereals, etc.)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., Vegetables, Fruits)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this category"
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text="Category icon/image"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']


# Product Model
class Product(models.Model):
    """
    Products listed by farmers for sale
    """
    
    # Status choices
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )
    
    # Unit choices
    UNIT_CHOICES = (
        ('kg', 'Kilogram'),
        ('bags', 'Bags'),
        ('bunches', 'Bunches'),
        ('pieces', 'Pieces'),
        ('liters', 'Liters'),
        ('tons', 'Tons'),
    )
    
    # Relationships
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'farmer'},
        related_name='products',
        help_text="Farmer who listed this product"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    
    # Product details
    name = models.CharField(
        max_length=200,
        help_text="Product name (e.g., Fresh Matooke)"
    )
    description = models.TextField(
        help_text="Detailed description of the product"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit in UGX"
    )
    quantity = models.IntegerField(
        help_text="Available quantity"
    )
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='kg'
    )
    
    # Location
    location = models.CharField(
        max_length=100,
        help_text="Where product is located (district/city)"
    )
    
    # Images
    image = models.ImageField(
        upload_to='products/',
        help_text="Main product image"
    )
    image2 = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Additional image"
    )
    image3 = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Additional image"
    )
    
    # Urgent sale features (NEW - ADD THESE THREE FIELDS)
    is_urgent = models.BooleanField(
        default=False,
        help_text="Mark as urgent sale (reduces post-harvest losses)"
    )
    urgent_discount = models.IntegerField(
        default=0,
        help_text="Discount percentage for urgent sales (0-50%)"
    )
    harvest_date = models.DateField(
        null=True,
        blank=True,
        help_text="When was this harvested"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.farmer.username}"
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']


class MarketPrice(models.Model):
    """
    Daily market prices for different products
    Helps farmers know fair market rates
    """
    product_name = models.CharField(
        max_length=200,
        help_text="Product name (e.g., Maize, Coffee, Matooke)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='market_prices'
    )
    market_location = models.CharField(
        max_length=100,
        help_text="Market location (e.g., Owino Market, Nakasero)"
    )
    
    # Price ranges
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Minimum price in UGX"
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Maximum price in UGX"
    )
    average_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Average market price in UGX"
    )
    
    unit = models.CharField(
        max_length=20,
        default='kg',
        help_text="Unit of measurement"
    )
    
    date_recorded = models.DateField(
        auto_now_add=True,
        help_text="Date when price was recorded"
    )
    
    source = models.CharField(
        max_length=200,
        default="Market Survey",
        help_text="Source of price information"
    )
    
    def __str__(self):
        return f"{self.product_name} - {self.market_location} ({self.date_recorded})"
    
    class Meta:
        verbose_name = "Market Price"
        verbose_name_plural = "Market Prices"
        ordering = ['-date_recorded']


class ExternalMarketPrice(models.Model):
    """
    Market prices fetched from external APIs (e.g., WFP, FAO)
    Provides reliable, third-party price data
    """
    SOURCE_CHOICES = (
        ('wfp', 'World Food Programme'),
        ('fao', 'FAO GIEWS'),
        ('ubos', 'Uganda Bureau of Statistics'),
        ('other', 'Other'),
    )
    
    product_name = models.CharField(
        max_length=200,
        help_text="Product/commodity name"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in UGX"
    )
    unit = models.CharField(
        max_length=20,
        default='kg',
        help_text="Unit of measurement"
    )
    market_location = models.CharField(
        max_length=100,
        help_text="Market or region"
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='wfp',
        help_text="Data source"
    )
    date_recorded = models.DateField(
        help_text="Date when price was recorded"
    )
    fetched_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When we fetched this data"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this price is still current"
    )
    
    # Additional metadata
    currency = models.CharField(
        max_length=10,
        default='UGX'
    )
    raw_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Original API response for reference"
    )
    
    def __str__(self):
        return f"{self.product_name} - {self.price} {self.currency}/{self.unit} ({self.source})"
    
    class Meta:
        verbose_name = "External Market Price"
        verbose_name_plural = "External Market Prices"
        ordering = ['-date_recorded', '-fetched_at']
        indexes = [
            models.Index(fields=['product_name', '-date_recorded']),
            models.Index(fields=['source', '-date_recorded']),
        ]



class CrowdsourcedPrice(models.Model):
    """
    Farmers report prices they're getting from buyers
    Helps prevent middleman exploitation
    """
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_prices'
    )
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    
    buyer_type = models.CharField(
        max_length=50,
        choices=[
            ('middleman', 'Middleman'),
            ('direct_consumer', 'Direct Consumer'),
            ('business', 'Business/Restaurant'),
            ('market', 'Market Vendor'),
        ]
    )
    
    location = models.CharField(max_length=100)
    market_name = models.CharField(max_length=200, blank=True)
    
    date_reported = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True, help_text="Additional context")
    
    def __str__(self):
        return f"{self.product_name} - UGX {self.price}/{self.unit} at {self.location}"
    
    class Meta:
        verbose_name = "Crowdsourced Price"
        verbose_name_plural = "Crowdsourced Prices"
        ordering = ['-date_reported']


# ==========================================
#  REVIEWS & RATINGS (Moved from reviews app)
# ==========================================

from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Order

class Review(models.Model):
    """
    Reviews and ratings for farmers
    Helps build trust in the marketplace
    """
    
    # Who is reviewing whom
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        help_text="User who wrote the review"
    )
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        limit_choices_to={'user_type': 'farmer'},
        help_text="Farmer being reviewed"
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='marketplace_review', # Changed related_name to avoid conflict during migration
        help_text="Order this review is for"
    )
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    # Review content
    comment = models.TextField(
        help_text="Review comment"
    )
    
    # Specific ratings
    product_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Quality of products (1-5)"
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Communication quality (1-5)"
    )
    delivery_speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Delivery speed (1-5)"
    )
    
    # Would recommend?
    would_recommend = models.BooleanField(
        default=True,
        help_text="Would you recommend this farmer?"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.farmer.username} - {self.rating}★"
    
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
        # unique_together = ['order'] # OneToOneField implies unique


class ReviewResponse(models.Model):
    """
    Allows farmers to respond to reviews
    """
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response'
    )
    response_text = models.TextField(
        help_text="Farmer's response to the review"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to review #{self.review.id}"
    
    class Meta:
        verbose_name = "Review Response"
        verbose_name_plural = "Review Responses"        