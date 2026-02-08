from django.contrib import admin
from .models import Category, Product, MarketPrice  # ADD MarketPrice here

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
admin.site.register(MarketPrice, MarketPriceAdmin)  # This was at the wrong place before