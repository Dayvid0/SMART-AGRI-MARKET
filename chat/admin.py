from django.contrib import admin
from .models import ChatThread, ChatMessage, NegotiatedDeal


class ChatMessageInline(admin.TabularInline):
    """
    Shows all messages inside a thread's admin detail view.
    Admins can read every message exchanged between buyers and sellers.
    """
    model = ChatMessage
    extra = 0
    readonly_fields = ['sender', 'content', 'is_read', 'sent_at']
    fields = ['sender', 'content', 'is_read', 'sent_at']
    ordering = ['sent_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    """
    Full admin panel for monitoring all buyer-seller negotiations.
    Admins can see the full conversation, filter by status, and search by participant.
    """
    list_display = [
        'id',
        'product_name',
        'buyer_username',
        'seller_username',
        'status',
        'message_count',
        'updated_at',
        'created_at',
    ]
    list_filter = ['status', 'created_at', 'product__category']
    search_fields = [
        'buyer__username',
        'seller__username',
        'product__name',
    ]
    readonly_fields = ['product', 'buyer', 'seller', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]
    ordering = ['-updated_at']
    list_per_page = 25

    fieldsets = (
        ('Participants', {
            'fields': ('product', 'buyer', 'seller'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Product')
    def product_name(self, obj):
        return obj.product.name

    @admin.display(description='Buyer')
    def buyer_username(self, obj):
        return obj.buyer.username

    @admin.display(description='Seller')
    def seller_username(self, obj):
        return obj.seller.username

    @admin.display(description='Messages')
    def message_count(self, obj):
        return obj.messages.count()

    # Admin actions
    @admin.action(description='Close selected threads')
    def close_threads(self, request, queryset):
        queryset.update(status='closed')

    @admin.action(description='Archive selected threads')
    def archive_threads(self, request, queryset):
        queryset.update(status='archived')

    @admin.action(description='Reopen selected threads')
    def reopen_threads(self, request, queryset):
        queryset.update(status='open')

    actions = ['close_threads', 'archive_threads', 'reopen_threads']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin view of individual messages — for searching specific content.
    """
    list_display = ['id', 'thread', 'sender', 'msg_type', 'short_content', 'offer_price', 'offer_status', 'is_read', 'sent_at']
    list_filter = ['msg_type', 'offer_status', 'is_read', 'sent_at']
    search_fields = ['sender__username', 'content', 'thread__product__name']
    readonly_fields = ['thread', 'sender', 'content', 'msg_type', 'offer_price', 'offer_quantity', 'offer_status', 'is_read', 'sent_at']
    ordering = ['-sent_at']

    @admin.display(description='Message')
    def short_content(self, obj):
        if obj.msg_type == 'offer':
            return f"💰 Price Offer: UGX {obj.offer_price} × {obj.offer_quantity}"
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content

    def has_add_permission(self, request):
        return False


@admin.register(NegotiatedDeal)
class NegotiatedDealAdmin(admin.ModelAdmin):
    """
    The paper trail of every agreed price between buyers and sellers.
    Admins can see: who agreed what price, for what product, and whether an order was placed.
    """
    list_display = [
        'id', 'product_name', 'buyer_name', 'seller_name',
        'agreed_price', 'agreed_quantity', 'deal_total',
        'order_status', 'accepted_at',
    ]
    list_filter = ['accepted_at']
    search_fields = [
        'thread__buyer__username', 'thread__seller__username',
        'thread__product__name',
    ]
    readonly_fields = [
        'thread', 'offer_message', 'agreed_price', 'agreed_quantity',
        'accepted_at', 'order',
    ]
    ordering = ['-accepted_at']

    @admin.display(description='Product')
    def product_name(self, obj):
        return obj.thread.product.name

    @admin.display(description='Buyer')
    def buyer_name(self, obj):
        return obj.thread.buyer.username

    @admin.display(description='Seller')
    def seller_name(self, obj):
        return obj.thread.seller.username

    @admin.display(description='Deal Total (UGX)')
    def deal_total(self, obj):
        return f"{obj.agreed_price * obj.agreed_quantity:,.0f}"

    @admin.display(description='Order')
    def order_status(self, obj):
        if obj.order:
            return f"#{obj.order.order_number} — {obj.order.get_status_display()}"
        return "⏳ Not yet ordered"

    def has_add_permission(self, request):
        return False
