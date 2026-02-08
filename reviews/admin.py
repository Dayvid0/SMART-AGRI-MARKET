from django.contrib import admin
from .models import Review, ReviewResponse

class ReviewResponseInline(admin.StackedInline):
    """
    Show farmer's response inside review detail
    """
    model = ReviewResponse
    extra = 0
    fields = ['response_text', 'created_at']
    readonly_fields = ['created_at']

class ReviewAdmin(admin.ModelAdmin):
    """
    Customize review admin
    """
    list_display = ['reviewer', 'farmer', 'rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    search_fields = ['reviewer__username', 'farmer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [ReviewResponseInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('reviewer', 'farmer', 'order', 'rating', 'comment')
        }),
        ('Detailed Ratings', {
            'fields': ('product_quality', 'communication', 'delivery_speed', 'would_recommend')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewResponse)