from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
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
        related_name='review',
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
        unique_together = ['order']  # One review per order


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