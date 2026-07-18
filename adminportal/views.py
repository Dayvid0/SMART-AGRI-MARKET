from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate, TruncWeek
from django.utils import timezone
from datetime import timedelta
import json

from accounts.models import User, VerificationRequest
from orders.models import Order, OrderItem
from marketplace.models import Product, Category


def staff_required(view_func):
    """Decorator that restricts access to staff/admin users only."""
    decorated = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='/accounts/login/'
    )(view_func)
    return decorated


@staff_required
def dashboard(request):
    """Main admin portal dashboard — summary stats."""
    today = timezone.now().date()
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # User stats
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    users_by_type = User.objects.values('user_type').annotate(count=Count('id')).order_by('-count')

    # Order stats
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=today).count()
    pending_orders = Order.objects.filter(status='pending').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    revenue_30d = Order.objects.filter(
        created_at__gte=thirty_days_ago, status__in=['completed', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Verification stats
    pending_verifications = VerificationRequest.objects.filter(status='pending').count()

    # Recent orders
    recent_orders = Order.objects.select_related('buyer', 'farmer').order_by('-created_at')[:10]

    # Recent registrations
    recent_users = User.objects.order_by('-date_joined')[:10]

    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'users_by_type': users_by_type,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'revenue_30d': revenue_30d,
        'pending_verifications': pending_verifications,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
    }
    return render(request, 'adminportal/dashboard.html', context)


@staff_required
def user_management(request):
    """List and manage all users."""
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')

    if query:
        users = users.filter(username__icontains=query) | \
                users.filter(email__icontains=query) | \
                users.filter(phone__icontains=query)
    if role:
        users = users.filter(user_type=role)
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'verified':
        users = users.filter(is_verified=True)

    context = {
        'users': users,
        'query': query,
        'role': role,
        'status_filter': status_filter,
        'user_types': User.USER_TYPES,
        'total_count': users.count(),
    }
    return render(request, 'adminportal/users.html', context)


@staff_required
def toggle_user_status(request, user_id):
    """Activate or deactivate a user account."""
    if request.method != 'POST':
        return redirect('adminportal:user_management')
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('adminportal:user_management')
    user.is_active = not user.is_active
    user.save()
    action = "activated" if user.is_active else "deactivated"
    messages.success(request, f"Account for {user.username} has been {action}.")
    return redirect('adminportal:user_management')


@staff_required
def verification_queue(request):
    """Show all pending identity verification requests."""
    status_filter = request.GET.get('status', 'pending')
    verifications = VerificationRequest.objects.select_related('user').order_by('-submitted_at')
    if status_filter:
        verifications = verifications.filter(status=status_filter)
    context = {
        'verifications': verifications,
        'status_filter': status_filter,
        'pending_count': VerificationRequest.objects.filter(status='pending').count(),
    }
    return render(request, 'adminportal/verifications.html', context)


@staff_required
def approve_verification(request, vr_id):
    """Approve a verification request."""
    if request.method != 'POST':
        return redirect('adminportal:verification_queue')
    vr = get_object_or_404(VerificationRequest, pk=vr_id)
    vr.status = 'approved'
    vr.reviewed_at = timezone.now()
    vr.save()
    vr.user.is_verified = True
    vr.user.save()
    messages.success(request, f"{vr.user.username}'s identity has been verified and approved.")
    return redirect('adminportal:verification_queue')


@staff_required
def reject_verification(request, vr_id):
    """Reject a verification request."""
    if request.method != 'POST':
        return redirect('adminportal:verification_queue')
    vr = get_object_or_404(VerificationRequest, pk=vr_id)
    vr.status = 'rejected'
    vr.reviewed_at = timezone.now()
    vr.save()
    messages.warning(request, f"{vr.user.username}'s verification request has been rejected.")
    return redirect('adminportal:verification_queue')


@staff_required
def order_overview(request):
    """Show all orders with filtering."""
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()

    orders = Order.objects.select_related('buyer', 'farmer').order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    if query:
        orders = orders.filter(order_number__icontains=query)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'query': query,
        'status_choices': Order.STATUS_CHOICES,
        'total_count': orders.count(),
    }
    return render(request, 'adminportal/orders.html', context)


@staff_required
def analytics(request):
    """Full analytics dashboard with chart data."""
    today = timezone.now().date()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    seven_days_ago = timezone.now() - timedelta(days=7)

    # ── Revenue over last 30 days (daily) ──
    revenue_qs = (
        Order.objects
        .filter(created_at__gte=thirty_days_ago, status__in=['completed', 'delivered'])
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Sum('total_amount'))
        .order_by('day')
    )
    revenue_labels = [str(r['day']) for r in revenue_qs]
    revenue_data   = [float(r['total'] or 0) for r in revenue_qs]

    # ── User registrations over last 30 days ──
    user_qs = (
        User.objects
        .filter(date_joined__gte=thirty_days_ago)
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    user_labels = [str(u['day']) for u in user_qs]
    user_data   = [u['count'] for u in user_qs]

    # ── Order status breakdown (donut) ──
    order_status_qs = (
        Order.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    status_labels = [o['status'].title() for o in order_status_qs]
    status_data   = [o['count'] for o in order_status_qs]

    # ── Users by role (bar) ──
    role_qs = User.objects.values('user_type').annotate(count=Count('id')).order_by('-count')
    role_labels = [r['user_type'].replace('_', ' ').title() for r in role_qs]
    role_data   = [r['count'] for r in role_qs]

    # ── Top 10 products by order volume ──
    top_products = (
        OrderItem.objects
        .values('product__name')
        .annotate(units=Sum('quantity'), revenue=Sum('subtotal'))
        .order_by('-units')[:10]
    )
    top_product_labels  = [p['product__name'] or 'Unknown' for p in top_products]
    top_product_units   = [float(p['units'] or 0) for p in top_products]
    top_product_revenue = [float(p['revenue'] or 0) for p in top_products]

    # ── Orders per district (top 10) ──
    district_qs = (
        Order.objects
        .exclude(farmer__district='')
        .values('farmer__district')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    district_labels = [d['farmer__district'] for d in district_qs]
    district_data   = [d['count'] for d in district_qs]

    # ── KPI summary ──
    total_revenue = Order.objects.filter(
        status__in=['completed', 'delivered']
    ).aggregate(t=Sum('total_amount'))['t'] or 0
    avg_order_value = Order.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0
    total_products  = Product.objects.filter(status='available').count()
    verified_users  = User.objects.filter(is_verified=True).count()

    context = {
        # Chart data (serialised to JSON for Chart.js)
        'revenue_labels':        json.dumps(revenue_labels),
        'revenue_data':          json.dumps(revenue_data),
        'user_labels':           json.dumps(user_labels),
        'user_data':             json.dumps(user_data),
        'status_labels':         json.dumps(status_labels),
        'status_data':           json.dumps(status_data),
        'role_labels':           json.dumps(role_labels),
        'role_data':             json.dumps(role_data),
        'top_product_labels':    json.dumps(top_product_labels),
        'top_product_units':     json.dumps(top_product_units),
        'top_product_revenue':   json.dumps(top_product_revenue),
        'district_labels':       json.dumps(district_labels),
        'district_data':         json.dumps(district_data),
        # KPI cards
        'total_revenue':    total_revenue,
        'avg_order_value':  avg_order_value,
        'total_products':   total_products,
        'verified_users':   verified_users,
        'total_users':      User.objects.count(),
        'total_orders':     Order.objects.count(),
        'pending_verifications': VerificationRequest.objects.filter(status='pending').count(),
    }
    return render(request, 'adminportal/analytics.html', context)
