from django.contrib import admin
from .models import Category, Product, MarketPrice, ExternalMarketPrice, CrowdsourcedPrice, Review, ReviewResponse

# Customize Category admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

# Customize Product admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'category', 'price', 'quantity', 'status', 'is_urgent', 'created_at']  # Added is_urgent
    list_filter = ['category', 'status', 'is_urgent', 'created_at']  # Added is_urgent
    search_fields = ['name', 'description', 'farmer__username']
    list_editable = ['status', 'is_urgent']  # Added is_urgent for quick editing

# Customize Market Price admin
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'market_location', 'average_price', 'unit', 'date_recorded']
    list_filter = ['category', 'market_location', 'date_recorded']
    search_fields = ['product_name', 'market_location']

# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(MarketPrice, MarketPriceAdmin)

# External Market Prices (WFP API)
@admin.register(ExternalMarketPrice)
class ExternalMarketPriceAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'unit', 'market_location', 'source', 'date_recorded', 'is_active']
    list_filter = ['source', 'is_active', 'date_recorded']
    search_fields = ['product_name', 'market_location']

# Crowdsourced Prices
@admin.register(CrowdsourcedPrice)
class CrowdsourcedPriceAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'unit', 'location', 'reporter', 'date_reported', 'is_verified']
    list_filter = ['buyer_type', 'is_verified', 'date_reported']
    search_fields = ['product_name', 'location']
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'farmer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'farmer__username', 'comment']

@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'created_at']
    search_fields = ['response_text']
