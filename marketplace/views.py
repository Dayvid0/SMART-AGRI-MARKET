from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, Category, AgriNews  # Assuming these are your models
import requests # For Weather API

@login_required
def farmer_dashboard(request):
    """
    Advanced Farmer Dashboard: Merges product management with Agri-Intelligence
    """
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can access this page!')
        return redirect('home')
    
    # --- CORE DATA ---
    products = Product.objects.filter(farmer=request.user)
    orders_received = Order.objects.filter(farmer=request.user).order_by('-created_at')[:5]
    
    # --- STATISTICS ---
    stats = {
        'total': products.count(),
        'available': products.filter(status='available').count(),
        'pending_orders': Order.objects.filter(farmer=request.user, status='pending').count(),
        'total_revenue': sum(o.total_price for o in Order.objects.filter(farmer=request.user, status='completed'))
    }

    # --- AGRI-INTELLIGENCE: Weather (Example: Kampala) ---
    # In a real app, replace with request.user.profile.location
    weather_data = {}
    try:
        api_key = "YOUR_OPENWEATHER_API_KEY"
        city = request.user.location or "Kampala"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5).json()
        weather_data = {
            'temp': response['main']['temp'],
            'desc': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon']
        }
    except:
        weather_data = {'temp': '--', 'desc': 'Weather unavailable', 'icon': ''}

    # --- AGRI-PULSE: Latest Govt News & Alerts ---
    govt_updates = AgriNews.objects.filter(category='govt').order_by('-date_posted')[:3]

    context = {
        'products': products,
        'orders_received': orders_received,
        'stats': stats,
        'weather': weather_data,
        'govt_updates': govt_updates,
    }
    return render(request, 'marketplace/farmer_dashboard.html', context)

@login_required
def add_product(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can add products!')
        return redirect('home')
    
    if request.method == 'POST':
        # Using a more robust way to handle the boolean check for 'is_urgent'
        Product.objects.create(
            farmer=request.user,
            category_id=request.POST.get('category'),
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            unit=request.POST.get('unit'),
            location=request.POST.get('location'),
            image=request.FILES.get('image'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),
            is_urgent=request.POST.get('is_urgent') == 'on',
            urgent_discount=request.POST.get('urgent_discount') or 0,
            harvest_date=request.POST.get('harvest_date') or None,
            status='available'
        )
        messages.success(request, 'Product listed successfully!')
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
        
        if request.POST.get('harvest_date'):
            product.harvest_date = request.POST.get('harvest_date')
        
        # Image Update Logic
        for i in ['', '2', '3']:
            field = f'image{i}' if i else 'image'
            if request.FILES.get(field):
                setattr(product, field, request.FILES.get(field))
        
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('farmer_dashboard')
    
    return render(request, 'marketplace/edit_product.html', {
        'product': product, 
        'categories': Category.objects.all()
    })

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product removed.')
        return redirect('farmer_dashboard')
    return render(request, 'marketplace/delete_product.html', {'product': product})