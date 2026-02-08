from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Show order items inside the order detail page
    """
    model = OrderItem
    extra = 0  # Don't show empty forms
    readonly_fields = ['subtotal']
    fields = ['product', 'quantity', 'unit_price', 'subtotal']

class OrderAdmin(admin.ModelAdmin):
    """
    Customize order admin
    """
    list_display = ['order_number', 'buyer', 'farmer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'buyer__username', 'farmer__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'buyer', 'farmer', 'status')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'delivery_phone', 'notes')
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)