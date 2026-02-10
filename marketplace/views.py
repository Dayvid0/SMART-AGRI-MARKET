from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Max, Min, Count
from datetime import date, timedelta
from django.db.models import Count

from .models import Product, Category, MarketPrice, CrowdsourcedPrice
from orders.models import Order
from accounts.models import FarmerProfile

# --- MARKETPLACE VIEWS ---

def home(request):
    """
    Homepage view - displays featured products and categories
    """
    featured_products = Product.objects.filter(status='available').order_by('-created_at')[:6]
    categories = Category.objects.all()[:6]
    total_products = Product.objects.filter(status='available').count()
    total_farmers = Product.objects.values('farmer').distinct().count()
    
    top_farmers = FarmerProfile.objects.filter(rating_average__gt=0).order_by('-rating_average')[:3]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'total_products': total_products,
        'total_farmers': total_farmers,
        'top_farmers': top_farmers,
    }
    return render(request, 'marketplace/home.html', context)


def product_list(request):
    """
    Display all products with search and filter functionality
    """
    products = Product.objects.filter(status='available')
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    location = request.GET.get('location')
    urgent_only = request.GET.get('urgent')
    
    if category_id:
        products = products.filter(category_id=category_id)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    if location:
        products = products.filter(location__icontains=location)
    if urgent_only:
        products = products.filter(is_urgent=True)
    
    urgent_products = Product.objects.filter(status='available', is_urgent=True)[:4]
    categories = Category.objects.all()
    locations = Product.objects.values_list('location', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
        'locations': locations,
        'selected_category': category_id,
        'search_query': search_query,
        'selected_location': location,
        'urgent_products': urgent_products,
        'urgent_only': urgent_only,
    }
    return render(request, 'marketplace/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status='available')
    related_products = Product.objects.filter(category=product.category, status='available').exclude(pk=pk)[:4]
    return render(request, 'marketplace/product_detail.html', {'product': product, 'related_products': related_products})


# --- PRICE INTELLIGENCE VIEWS ---

def market_prices(request):
    """
    Official market prices
    """
    week_ago = date.today() - timedelta(days=7)
    latest_prices = MarketPrice.objects.filter(date_recorded__gte=week_ago)
    categories = Category.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        latest_prices = latest_prices.filter(category_id=category_id)
    
    price_data = latest_prices.values('product_name', 'unit').annotate(
        avg_min=Avg('min_price'),
        avg_max=Avg('max_price'),
        avg_price=Avg('average_price')
    ).order_by('product_name')
    
    context = {
        'price_data': price_data,
        'categories': categories,
        'selected_category': category_id,
        'latest_prices': latest_prices,
    }
    return render(request, 'marketplace/market_prices.html', context)


@login_required
def report_price(request):
    """
    Farmers report prices they're actually getting in the field
    """
    if request.method == 'POST':
        CrowdsourcedPrice.objects.create(
            reporter=request.user,
            product_name=request.POST.get('product_name'),
            price=request.POST.get('price'),
            unit=request.POST.get('unit'),
            buyer_type=request.POST.get('buyer_type'),
            location=request.POST.get('location'),
            market_name=request.POST.get('market_name'),
            notes=request.POST.get('notes')
        )
        messages.success(request, 'Thank you! Your price report helps other farmers.')
        return redirect('price_tracker')
    
    return render(request, 'marketplace/report_price.html')


def price_tracker(request):
    """
    Display crowdsourced prices from farmers
    """
    recent_date = date.today() - timedelta(days=30)
    recent_prices = CrowdsourcedPrice.objects.filter(date_reported__gte=recent_date)
    
    product_filter = request.GET.get('product')
    location_filter = request.GET.get('location')
    
    if product_filter:
        recent_prices = recent_prices.filter(product_name__icontains=product_filter)
    if location_filter:
        recent_prices = recent_prices.filter(location__icontains=location_filter)
    
    price_summary = recent_prices.values('product_name', 'unit').annotate(
        avg_price=Avg('price'),
        min_price=Min('price'),
        max_price=Max('price'),
        report_count=Count('id')
    ).order_by('product_name')
    
    products = CrowdsourcedPrice.objects.values_list('product_name', flat=True).distinct()
    locations = CrowdsourcedPrice.objects.values_list('location', flat=True).distinct()
    
    context = {
        'price_summary': price_summary,
        'recent_prices': recent_prices[:20],
        'products': products,
        'locations': locations,
        'product_filter': product_filter,
        'location_filter': location_filter,
    }
    return render(request, 'marketplace/price_tracker.html', context)


# --- FARMER MANAGEMENT VIEWS ---

@login_required
def farmer_dashboard(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can access this page!')
        return redirect('home')
    
    products = Product.objects.filter(farmer=request.user)
    orders_received = Order.objects.filter(farmer=request.user).order_by('-created_at')[:5]
    
    context = {
        'products': products,
        'orders_received': orders_received,
        'total_products': products.count(),
        'available_products': products.filter(status='available').count(),
        'pending_orders': Order.objects.filter(farmer=request.user, status='pending').count(),
    }
    return render(request, 'marketplace/farmer_dashboard.html', context)


@login_required
def add_product(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can add products!')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        is_urgent = request.POST.get('is_urgent') == 'on'
        harvest_date = request.POST.get('harvest_date')
        
        Product.objects.create(
            farmer=request.user,
            category_id=request.POST.get('category'),
            name=name,
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            unit=request.POST.get('unit'),
            location=request.POST.get('location'),
            image=request.FILES.get('image'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),
            is_urgent=is_urgent,
            urgent_discount=request.POST.get('urgent_discount') or 0,
            harvest_date=harvest_date if harvest_date else None,
            status='available'
        )
        messages.success(request, f'Product "{name}" added successfully!')
        return redirect('farmer_dashboard')
    
    return render(request, 'marketplace/add_product.html', {'categories': Category.objects.all()})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.unit = request.POST.get('unit')
        product.location = request.POST.get('location')
        product.status = request.POST.get('status')
        product.is_urgent = request.POST.get('is_urgent') == 'on'
        product.urgent_discount = request.POST.get('urgent_discount') or 0
        
        harvest_date = request.POST.get('harvest_date')
        if harvest_date:
            product.harvest_date = harvest_date
        
        if request.FILES.get('image'): product.image = request.FILES.get('image')
        if request.FILES.get('image2'): product.image2 = request.FILES.get('image2')
        if request.FILES.get('image3'): product.image3 = request.FILES.get('image3')
        
        product.save()
        messages.success(request, f'Product "{product.name}" updated!')
        return redirect('farmer_dashboard')
    
    return render(request, 'marketplace/edit_product.html', {'product': product, 'categories': Category.objects.all()})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted!')
        return redirect('farmer_dashboard')
    return render(request, 'marketplace/delete_product.html', {'product': product})