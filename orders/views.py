from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem, DeliveryRequest
from accounts.models import TransporterProfile
from marketplace.models import Product
from notifications.helpers import (
    notify_new_order,
    notify_order_status_changed,
    notify_order_cancelled_by_buyer,
    notify_delivery_accepted,
)
from chat.models import NegotiatedDeal
import random
import string
from datetime import datetime

def generate_order_number():
    """Generate unique order number like ORD-20250208-A1B2"""
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_part}-{random_part}"





# =============================================
# DELIVERY REQUEST VIEWS
# =============================================

@login_required
def request_delivery(request, order_id):
    """
    Farmer creates a delivery request for a confirmed order,
    opening it to transporters in the area.
    """
    order = get_object_or_404(Order, pk=order_id, farmer=request.user)

    if order.status not in ('confirmed', 'processing'):
        messages.error(request, 'Delivery can only be requested for confirmed or processing orders.')
        return redirect('orders:order_detail', order_id=order_id)

    if hasattr(order, 'delivery_request'):
        messages.info(request, 'A delivery request already exists for this order.')
        return redirect('orders:delivery_detail', delivery_id=order.delivery_request.id)

    if request.method == 'POST':
        pickup_district = request.POST.get('pickup_district', '').strip()
        delivery_district = request.POST.get('delivery_district', '').strip()
        pickup_address = request.POST.get('pickup_address', '').strip()
        offered_price_raw = request.POST.get('offered_price', '0').strip()
        notes = request.POST.get('notes', '').strip()

        try:
            offered_price = float(offered_price_raw)
            if offered_price < 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid transport fee.')
            return render(request, 'orders/request_delivery.html', {'order': order})

        dr = DeliveryRequest.objects.create(
            order=order,
            pickup_district=pickup_district or order.farmer.district or 'Kampala',
            delivery_district=delivery_district,
            pickup_address=pickup_address,
            offered_price=offered_price,
            notes=notes,
            status='open',
        )
        messages.success(
            request,
            'Delivery request posted! Transporters in the area will be notified.'
        )
        return redirect('orders:delivery_detail', delivery_id=dr.id)

    from accounts.constants import DISTRICT_CHOICES
    return render(request, 'orders/request_delivery.html', {
        'order': order,
        'district_choices': DISTRICT_CHOICES,
    })


@login_required
def delivery_detail(request, delivery_id):
    """View a delivery request's details and available transporters."""
    delivery = get_object_or_404(DeliveryRequest, pk=delivery_id)
    order = delivery.order

    if request.user not in (order.farmer, order.buyer) and request.user != delivery.transporter:
        if request.user.user_type != 'transporter':
            messages.error(request, 'Access denied.')
            return redirect('home')

    # Find transporters whose coverage includes both districts
    available_transporters = []
    if delivery.status == 'open':
        pickup = delivery.pickup_district.lower()
        dest = delivery.delivery_district.lower()
        for tp in TransporterProfile.objects.select_related('user').filter(user__is_active=True):
            districts = [d.lower() for d in tp.get_districts_list()]
            if pickup in districts or dest in districts:
                available_transporters.append(tp)

    return render(request, 'orders/delivery_detail.html', {
        'delivery': delivery,
        'order': order,
        'available_transporters': available_transporters,
    })


@login_required
def accept_delivery(request, delivery_id):
    """Transporter accepts an open delivery request."""
    delivery = get_object_or_404(DeliveryRequest, pk=delivery_id, status='open')

    if request.user.user_type != 'transporter':
        messages.error(request, 'Only registered transporters can accept delivery requests.')
        return redirect('orders:delivery_detail', delivery_id=delivery_id)

    if request.method == 'POST':
        delivery.transporter = request.user
        delivery.status = 'assigned'
        delivery.assigned_at = timezone.now()
        delivery.save()
        
        # Notify farmer and buyer
        try:
            notify_delivery_accepted(delivery)
        except Exception:
            pass
            
        messages.success(request, 'You have accepted this delivery. Contact the farmer to coordinate pickup.')
        return redirect('orders:delivery_detail', delivery_id=delivery_id)
        
    return render(request, 'orders/accept_delivery_confirm.html', {'delivery': delivery})


@login_required
def update_delivery_status(request, delivery_id):
    """Transporter updates delivery status (assigned -> in_transit -> delivered)"""
    delivery = get_object_or_404(DeliveryRequest, pk=delivery_id)
    
    if request.user != delivery.transporter:
        messages.error(request, 'You do not have permission to update this delivery.')
        return redirect('marketplace:transporter_dashboard')
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['assigned', 'in_transit', 'delivered']
        
        if new_status in valid_statuses:
            delivery.status = new_status
            if new_status == 'delivered':
                delivery.delivered_at = timezone.now()
                # Auto-complete the order
                order = delivery.order
                order.status = 'completed'
                order.save()
            delivery.save()
            messages.success(request, f'Delivery status updated to {delivery.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status update.')
            
    return redirect('marketplace:transporter_dashboard')


@login_required
def place_order(request, product_id):
    """
    Place an order for a single product. Handles negotiated deals.
    """
    product = get_object_or_404(Product, pk=product_id, status='available')
    
    # Prevent farmer from ordering their own products
    if request.user == product.farmer:
        messages.error(request, 'You cannot order your own products!')
        return redirect('marketplace:product_detail', pk=product_id)
        
    deal_id = request.GET.get('deal_id') or request.POST.get('deal_id')
    deal = None
    if deal_id:
        deal = get_object_or_404(NegotiatedDeal, pk=deal_id, thread__buyer=request.user, thread__product=product)
        if deal.order:
            messages.error(request, 'This deal has already been used to place an order.')
            return redirect('marketplace:product_detail', pk=product_id)
    
    if request.method == 'POST':
        if deal:
            quantity = deal.agreed_quantity
            unit_price = deal.agreed_price
        else:
            quantity = int(request.POST.get('quantity', 1))
            unit_price = product.price
            
        delivery_address = request.POST.get('delivery_address')
        delivery_phone = request.POST.get('delivery_phone')
        notes = request.POST.get('notes', '')
        
        # Validate quantity
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0!')
            return redirect('marketplace:product_detail', pk=product_id)
        
        if quantity > product.quantity:
            messages.error(request, f'Only {product.quantity} {product.unit} available!')
            return redirect('marketplace:product_detail', pk=product_id)
        
        # Calculate total
        total_amount = quantity * unit_price
        
        # Create order
        order = Order.objects.create(
            buyer=request.user,
            farmer=product.farmer,
            order_number=generate_order_number(),
            status='pending',
            total_amount=total_amount,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            notes=notes
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price
        )
        
        # Update product quantity
        product.quantity -= quantity
        if product.quantity == 0:
            product.status = 'out_of_stock'
        product.save()
        
        if deal:
            deal.order = order
            deal.save(update_fields=['order'])
        
        # Notify the farmer about the new order
        try:
            notify_new_order(order)
        except Exception:
            pass
        messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'product': product,
        'deal': deal
    }
    return render(request, 'orders/place_order.html', context)


@login_required
def order_detail(request, order_id):
    """
    View order details
    """
    order = get_object_or_404(Order, pk=order_id)
    
    # Only buyer or farmer can view order
    if request.user != order.buyer and request.user != order.farmer:
        messages.error(request, 'You do not have permission to view this order!')
        return redirect('home')
    
    context = {
        'order': order
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def my_orders(request):
    """
    View all orders for current user
    """
    # Orders I placed (as buyer)
    orders_placed = Order.objects.filter(buyer=request.user)
    
    # Orders I received (as farmer)
    orders_received = Order.objects.filter(farmer=request.user)
    
    context = {
        'orders_placed': orders_placed,
        'orders_received': orders_received
    }
    return render(request, 'orders/my_orders.html', context)


@login_required
def update_order_status(request, order_id):
    """
    Update order status (farmers only)
    """
    order = get_object_or_404(Order, pk=order_id)
    
    # Only farmer can update status
    if request.user != order.farmer:
        messages.error(request, 'Only the farmer can update order status!')
        return redirect('orders:order_detail', order_id=order_id)  # FIXED
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            # Notify buyer about the status change
            try:
                notify_order_status_changed(order)
            except Exception:
                pass
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status!')
    
    return redirect('orders:order_detail', order_id=order_id)  # FIXED


@login_required
def cancel_order(request, order_id):
    """
    Cancel an order
    """
    order = get_object_or_404(Order, pk=order_id)
    
    # Only buyer can cancel, and only if pending
    if request.user != order.buyer:
        messages.error(request, 'You can only cancel your own orders!')
        return redirect('orders:order_detail', order_id=order_id)  # FIXED
    
    if order.status != 'pending':
        messages.error(request, f'Cannot cancel order with status: {order.get_status_display()}')
        return redirect('orders:order_detail', order_id=order_id)  # FIXED
    
    # Restore product quantity
    for item in order.items.all():
        product = item.product
        product.quantity += item.quantity
        if product.status == 'out_of_stock':
            product.status = 'available'
        product.save()
    
    # Update order status
    order.status = 'cancelled'
    order.save()
    # Notify farmer that the buyer cancelled
    try:
        notify_order_cancelled_by_buyer(order)
    except Exception:
        pass
    messages.success(request, 'Order cancelled successfully!')
    return redirect('orders:order_detail', order_id=order_id)  # FIXED


