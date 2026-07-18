from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem, DeliveryRequest
from accounts.models import TransporterProfile
from marketplace.models import Product
from inputs.models import AgriculturalInput
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
        # Check active deliveries limit
        active_deliveries = DeliveryRequest.objects.filter(
            transporter=request.user,
            status__in=['assigned', 'in_transit']
        ).count()
        if active_deliveries >= 3:
            messages.error(request, 'You cannot have more than 3 active deliveries at a time.')
            return redirect('orders:delivery_detail', delivery_id=delivery_id)

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
                # Auto-update the order to delivered (not completed, buyer must confirm)
                order = delivery.order
                order.status = 'delivered'
                order.save()
            delivery.save()
            messages.success(request, f'Delivery status updated to {delivery.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status update.')
            
    return redirect('marketplace:transporter_dashboard')


@login_required
def place_order(request, product_id=None, input_id=None):
    """
    Place an order for a single product or input. Handles negotiated deals.
    """
    product = None
    input_item = None
    seller = None
    item_name = ""
    unit = ""
    available_qty = 0
    price_per_unit = 0
    cancel_url = "/"

    if product_id:
        product = get_object_or_404(Product, pk=product_id, status='available')
        seller = product.farmer
        item_name = product.name
        unit = product.unit
        available_qty = product.quantity
        price_per_unit = product.price
        from django.urls import reverse
        cancel_url = reverse('marketplace:product_detail', args=[product.pk])
    elif input_id:
        input_item = get_object_or_404(AgriculturalInput, pk=input_id, status='available')
        seller = input_item.supplier
        item_name = input_item.name
        unit = input_item.unit
        available_qty = input_item.quantity_available
        price_per_unit = input_item.price
        from django.urls import reverse
        cancel_url = reverse('inputs:input_detail', args=[input_item.pk])
    else:
        return redirect('home')

    # Prevent ordering own products
    if request.user == seller:
        messages.error(request, 'You cannot order your own products!')
        return redirect(cancel_url)
        
    deal_id = request.GET.get('deal_id') or request.POST.get('deal_id')
    deal = None
    if deal_id and product:
        deal = get_object_or_404(NegotiatedDeal, pk=deal_id, thread__buyer=request.user, thread__product=product)
        if deal.order:
            messages.error(request, 'This deal has already been used to place an order.')
            return redirect(cancel_url)
        price_per_unit = deal.agreed_price
    
    if request.method == 'POST':
        from django.db import transaction
        with transaction.atomic():
            # Lock the record for update
            if product_id:
                product = get_object_or_404(Product.objects.select_for_update(), pk=product_id, status='available')
                available_qty = product.quantity
            elif input_id:
                input_item = get_object_or_404(AgriculturalInput.objects.select_for_update(), pk=input_id, status='available')
                available_qty = input_item.quantity_available

            if deal:
                quantity = deal.agreed_quantity
            else:
                quantity = int(request.POST.get('quantity', 1))
                
            delivery_address = request.POST.get('delivery_address')
            delivery_phone = request.POST.get('delivery_phone')
            delivery_method = request.POST.get('delivery_method', 'self_pickup')
            notes = request.POST.get('notes', '')
            
            # Validate quantity
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than 0!')
                return redirect(cancel_url)
            
            if quantity > available_qty:
                messages.error(request, f'Only {available_qty} {unit} available!')
                return redirect(cancel_url)
            
            # Calculate total
            total_amount = quantity * price_per_unit
            
            # Create order
            order = Order.objects.create(
                buyer=request.user,
                farmer=seller,
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
                input_product=input_item,
                quantity=quantity,
                unit_price=price_per_unit
            )
            
            # Update product quantity
            if product:
                product.quantity -= quantity
                if product.quantity == 0:
                    product.status = 'out_of_stock'
                product.save()
            elif input_item:
                input_item.quantity_available -= quantity
                if input_item.quantity_available == 0:
                    input_item.status = 'out_of_stock'
                input_item.save()
            
            # Mark deal as used
            if deal:
                deal.order = order
                deal.save()
                
            # Notify the seller about the new order
            try:
                notify_new_order(order)
            except Exception:
                pass
                
            # If platform transport selected, create delivery request automatically
            if delivery_method == 'platform':
                dr = DeliveryRequest.objects.create(
                    order=order,
                    pickup_district=order.farmer.district or 'Kampala',
                    delivery_district='TBD', # Should be determined by buyer profile or input
                    status='open',
                    notes='Auto-requested by buyer during checkout',
                    offered_price=0
                )
                messages.success(request, f'Order placed! A delivery request has been broadcasted to platform transporters.')
            else:
                messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
                
            return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'product': product,
        'input_item': input_item,
        'deal': deal,
        'item_name': item_name,
        'unit': unit,
        'available_qty': available_qty,
        'price_per_unit': price_per_unit,
        'seller': seller,
        'cancel_url': cancel_url,
    }
    return render(request, 'orders/place_order.html', context)

@login_required
def confirm_receipt(request, order_id):
    """
    Buyer confirms receipt of a delivered order.
    Transitions order from 'delivered' to 'completed'.
    """
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    
    if request.method == 'POST':
        if order.status == 'delivered':
            order.status = 'completed'
            order.save()
            messages.success(request, 'Order marked as completed. Thank you for confirming receipt!')
            # Notify the seller that order is completed
            notify_order_status_changed(order)
        else:
            messages.error(request, 'You can only confirm receipt for delivered orders.')
            
    return redirect('orders:order_detail', order_id=order.id)


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
        if item.product:
            product = item.product
            product.quantity += item.quantity
            if product.status == 'out_of_stock':
                product.status = 'available'
            product.save()
        elif item.input_product:
            product = item.input_product
            product.quantity_available += item.quantity
            product.save()
    
    # Update order status
    order.status = 'cancelled'
    
    # Save cancellation reason if provided
    reason = request.POST.get('cancellation_reason', '').strip()
    if reason:
        order.cancellation_reason = reason
        
    order.save()
    # Notify farmer that the buyer cancelled
    try:
        notify_order_cancelled_by_buyer(order)
    except Exception:
        pass
    messages.success(request, 'Order cancelled successfully!')
    return redirect('orders:order_detail', order_id=order_id)  # FIXED


