"""
notifications/helpers.py

Central helper for creating in-app notifications across all apps.
Import and call these functions wherever an event occurs.

All notification types already defined in Notification model:
  'news', 'product', 'weather', 'system', 'admin'

We add two new logical types:
  'order'  → maps to 'system' type
  'chat'   → maps to 'system' type
"""
from .models import Notification


# ──────────────────────────────────────────────
# ORDER NOTIFICATIONS
# ──────────────────────────────────────────────

def notify_new_order(order):
    """
    Fired when a buyer places a new order.
    → Farmer gets alerted.
    """
    Notification.objects.create(
        user=order.farmer,
        notification_type='order',
        title='🛒 New Order Received',
        message=(
            f'{order.buyer.username} placed Order #{order.order_number} for '
            f'{order.items.first().product.name if order.items.exists() else "your product"}. '
            f'Total: UGX {order.total_amount:,.0f}.'
        ),
        link=f'/orders/detail/{order.id}/',
    )


def notify_order_status_changed(order):
    """
    Fired when the farmer updates the order status.
    → Buyer gets the update.
    """
    STATUS_EMOJIS = {
        'confirmed': '✅',
        'processing': '⚙️',
        'completed': '🎉',
        'cancelled': '❌',
    }
    emoji = STATUS_EMOJIS.get(order.status, '📦')
    Notification.objects.create(
        user=order.buyer,
        notification_type='order',
        title=f'{emoji} Order #{order.order_number} — {order.get_status_display()}',
        message=(
            f'Your order from {order.farmer.username} has been updated to '
            f'<strong>{order.get_status_display()}</strong>.'
        ),
        link=f'/orders/detail/{order.id}/',
    )


def notify_order_cancelled_by_buyer(order):
    """
    Fired when a buyer cancels their own order.
    → Farmer gets alerted so they don't keep goods on hold.
    """
    Notification.objects.create(
        user=order.farmer,
        notification_type='order',
        title='❌ Order Cancelled by Buyer',
        message=(
            f'Order #{order.order_number} from {order.buyer.username} has been cancelled. '
            'Your product stock has been restored.'
        ),
        link=f'/orders/detail/{order.id}/',
    )


# ──────────────────────────────────────────────
# DELIVERY NOTIFICATIONS
# ──────────────────────────────────────────────

def notify_delivery_accepted(delivery):
    """
    Fired when a transporter accepts a delivery request.
    → Farmer and buyer both notified.
    """
    order = delivery.order
    transporter = delivery.transporter

    # Notify farmer
    Notification.objects.create(
        user=order.farmer,
        notification_type='order',
        title='🚚 Transporter Assigned',
        message=(
            f'{transporter.username} has accepted the delivery for Order #{order.order_number}. '
            f'They will contact you for pickup coordination.'
        ),
        link=f'/orders/delivery/{delivery.id}/',
    )
    # Notify buyer
    Notification.objects.create(
        user=order.buyer,
        notification_type='order',
        title='🚚 Your Order is On Its Way!',
        message=(
            f'A transporter has been assigned for your Order #{order.order_number}. '
            'Your goods are being prepared for delivery.'
        ),
        link=f'/orders/detail/{order.id}/',
    )


# ──────────────────────────────────────────────
# CHAT / NEGOTIATION NOTIFICATIONS
# ──────────────────────────────────────────────

def notify_new_chat_message(message):
    """
    Fired when a new chat message is sent.
    → The OTHER participant in the thread gets notified.
    """
    thread = message.thread
    recipient = thread.seller if message.sender == thread.buyer else thread.buyer

    Notification.objects.create(
        user=recipient,
        notification_type='chat',
        title=f'💬 New Message from {message.sender.username}',
        message=(
            f'Regarding <strong>{thread.product.name}</strong>: '
            f'"{message.content[:80]}{"…" if len(message.content) > 80 else ""}"'
        ),
        link=f'/chat/room/{thread.id}/',
    )


def notify_chat_thread_closed(thread, closed_by):
    """
    Fired when a negotiation thread is closed.
    → The other participant gets notified.
    """
    recipient = thread.seller if closed_by == thread.buyer else thread.buyer
    Notification.objects.create(
        user=recipient,
        notification_type='chat',
        title='🔒 Negotiation Closed',
        message=(
            f'{closed_by.username} has closed the negotiation for '
            f'<strong>{thread.product.name}</strong>.'
        ),
        link=f'/chat/room/{thread.id}/',
    )


# ──────────────────────────────────────────────
# REVIEW NOTIFICATIONS
# ──────────────────────────────────────────────

def notify_new_review(review):
    """
    Fired when a buyer submits a review for a farmer.
    → Farmer gets notified.
    """
    stars = '⭐' * review.rating
    Notification.objects.create(
        user=review.farmer,
        notification_type='product',
        title=f'⭐ New Review — {review.rating}/5',
        message=(
            f'{review.reviewer.username} left you a {stars} review: '
            f'"{review.comment[:80]}{"…" if len(review.comment) > 80 else ""}"'
        ),
        link=f'/marketplace/reviews/farmer/{review.farmer.id}/',
    )
