from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from marketplace.models import Product
import random
import string
from datetime import datetime

def generate_order_number():
    """
    Generate unique order number like ORD-20250208-A1B2
    """
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_part}-{random_part}"

@login_required
def place_order(request, product_id):
    """
    Place an order for a single product
    """
    product = get_object_or_404(Product, pk=product_id, status='available')
    
    # Prevent farmer from ordering their own products
    if request.user == product.farmer:
        messages.error(request, 'You cannot order your own products!')
        return redirect('product_detail', pk=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        delivery_address = request.POST.get('delivery_address')
        delivery_phone = request.POST.get('delivery_phone')
        notes = request.POST.get('notes', '')
        
        # Validate quantity
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0!')
            return redirect('product_detail', pk=product_id)
        
        if quantity > product.quantity:
            messages.error(request, f'Only {product.quantity} {product.unit} available!')
            return redirect('product_detail', pk=product_id)
        
        # Calculate total
        unit_price = product.price
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
        
        messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
        return redirect('orders:order_detail', order_id=order.id)  # FIXED
    
    context = {
        'product': product
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
    
    messages.success(request, 'Order cancelled successfully!')
    return redirect('orders:order_detail', order_id=order_id)  # FIXED


