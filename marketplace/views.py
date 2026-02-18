from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Max, Min, Count
from datetime import date, timedelta
from django.db.models import Count

from .models import Product, Category, MarketPrice, CrowdsourcedPrice, ExternalMarketPrice
from orders.models import Order
from accounts.models import FarmerProfile
from .services.price_fetcher import combine_price_sources

# --- MARKETPLACE VIEWS ---

def home(request):
    """
    Homepage view - displays featured products, categories, news, weather, and user data
    """
    # Products & stats — uses your actual 'status' field
    featured_products = (
        Product.objects
        .filter(status='available')
        .select_related('category', 'farmer')
        .order_by('-created_at')[:4]
    )
    categories = Category.objects.all()[:12]
    total_products = Product.objects.filter(status='available').count()
    total_farmers = Product.objects.values('farmer').distinct().count()

    # Top rated farmers (keep existing logic)
    top_farmers = FarmerProfile.objects.filter(rating_average__gt=0).order_by('-rating_average')[:3]

    # Latest 3 approved news articles
    try:
        from news.models import News
        latest_news = (
            News.objects
            .filter(status='approved')
            .select_related('author')
            .order_by('-created_at')[:3]
        )
    except Exception:
        latest_news = []

    # Recommended products from same district as logged-in user
    recommended_products = []
    if request.user.is_authenticated and hasattr(request.user, 'district') and request.user.district:
        recommended_products = (
            Product.objects
            .filter(status='available', farmer__district=request.user.district)
            .exclude(farmer=request.user)
            .select_related('category', 'farmer')
            .order_by('-created_at')[:4]
        )

    # Recent orders for logged-in user
    recent_orders = []
    if request.user.is_authenticated:
        try:
            # Try buyer field first (orders placed by this user as a customer)
            recent_orders = (
                Order.objects
                .filter(buyer=request.user)
                .order_by('-created_at')[:3]
            )
        except Exception:
            try:
                # Fallback: orders received by this user as a farmer
                recent_orders = (
                    Order.objects
                    .filter(farmer=request.user)
                    .order_by('-created_at')[:3]
                )
            except Exception:
                recent_orders = []

    # HYBRID MARKET PRICES - Combine WFP API + Crowdsourced
    # Get recent external prices (last 7 days)
    week_ago = date.today() - timedelta(days=7)
    external_prices = ExternalMarketPrice.objects.filter(
        is_active=True,
        date_recorded__gte=week_ago
    ).order_by('-date_recorded')[:10]
    
    # Get recent crowdsourced prices
    crowdsourced_recent = CrowdsourcedPrice.objects.filter(
        date_reported__gte=week_ago
    ).order_by('-date_reported')[:10]
    
    # Convert external prices to dict format for combination
    external_price_dicts = [{
        'product_name': p.product_name,
        'price': p.price,
        'unit': p.unit,
        'market_location': p.market_location,
        'date_recorded': p.date_recorded,
        'source': 'WFP API'
    } for p in external_prices]
    
    # Combine both sources
    hybrid_prices = combine_price_sources(external_price_dicts, crowdsourced_recent)

    context = {
        'featured_products':    featured_products,
        'categories':           categories,
        'total_products':       total_products,
        'total_farmers':        total_farmers,
        'top_farmers':          top_farmers,
        'latest_news':          latest_news,
        'recommended_products': recommended_products,
        'recent_orders':        recent_orders,
        'hybrid_prices':        hybrid_prices,  # NEW: Hybrid price data
        'all_districts':        UGANDA_REGIONS, # Pass the regions dict or flat list
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


from .constants import UGANDA_REGIONS, DISTRICT_COORDINATES

def district_list(request):
    """
    Display interactive map and list of districts with stats.
    """
    from accounts.models import User
    from django.db.models import Count

    # Get farmer counts
    farmer_counts = User.objects.filter(user_type='farmer').values('district').annotate(count=Count('id'))
    stats = {item['district']: item['count'] for item in farmer_counts if item['district']}

    # Prepare structured data for template
    region_data = {}
    for region, districts in UGANDA_REGIONS.items():
        region_data[region] = []
        for district in districts:
            count = stats.get(district, 0)
            region_data[region].append({'name': district, 'count': count})

    context = {
        'region_data': region_data, # Use this structured data
        'coordinates': DISTRICT_COORDINATES,
        'mapbox_token': 'pk.eyJ1IjoibWF0cml4IiwiYSI6ImNs...placeholder...if_needed' 
    }
    return render(request, 'marketplace/district_list.html', context)

def farmer_list(request):
    """
    Display a list of all registered farmers grouped by region
    """
    from accounts.models import User
    
    # Use imported regions
    REGIONS = UGANDA_REGIONS
    
    farmers = User.objects.filter(user_type='farmer').select_related('farmer_profile')
    
    farmers_by_region = {region: [] for region in REGIONS.keys()}
    farmers_by_region['Other'] = []
    
    for farmer in farmers:
        district = farmer.district
        placed = False
        if district:
            for region, districts in REGIONS.items():
                if district in districts:
                    farmers_by_region[region].append(farmer)
                    placed = True
                    break
        
        if not placed:
            farmers_by_region['Other'].append(farmer)
            
    # Remove empty regions
    farmers_by_region = {k: v for k, v in farmers_by_region.items() if v}
    
    context = {
        'farmers_by_region': farmers_by_region,
    }
    return render(request, 'marketplace/farmer_list.html', context)


# ==========================================
#  REVIEWS VIEWS (Moved from reviews app)
# ==========================================

from .models import Review, ReviewResponse

@login_required
def create_review(request, order_id):
    """
    Create a review for a completed order
    """
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    
    # Check if order is completed
    if order.status != 'completed':
        messages.error(request, 'You can only review completed orders!')
        return redirect('orders:order_detail', order_id=order_id)
    
    # Check if review already exists
    # Use 'marketplace_review' related_name from new model definition
    if hasattr(order, 'marketplace_review'):
        messages.error(request, 'You have already reviewed this order!')
        return redirect('orders:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        product_quality = int(request.POST.get('product_quality'))
        communication = int(request.POST.get('communication'))
        delivery_speed = int(request.POST.get('delivery_speed'))
        would_recommend = request.POST.get('would_recommend') == 'on'
        
        # Create review
        review = Review.objects.create(
            reviewer=request.user,
            farmer=order.farmer,
            order=order,
            rating=rating,
            comment=comment,
            product_quality=product_quality,
            communication=communication,
            delivery_speed=delivery_speed,
            would_recommend=would_recommend
        )
        
        # Update farmer's average rating
        update_farmer_rating(order.farmer)
        
        messages.success(request, 'Review submitted successfully!')
        return redirect('orders:order_detail', order_id=order_id)
    
    context = {
        'order': order
    }
    # Template path updated to marketplace/reviews
    return render(request, 'marketplace/reviews/create_review.html', context)


@login_required
def farmer_reviews(request, farmer_id):
    """
    View all reviews for a specific farmer
    """
    from accounts.models import User
    farmer = get_object_or_404(User, pk=farmer_id, user_type='farmer')
    
    reviews = Review.objects.filter(farmer=farmer).select_related('reviewer', 'order')
    
    # Calculate statistics
    total_reviews = reviews.count()
    if total_reviews > 0:
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        avg_quality = reviews.aggregate(Avg('product_quality'))['product_quality__avg']
        avg_communication = reviews.aggregate(Avg('communication'))['communication__avg']
        avg_delivery = reviews.aggregate(Avg('delivery_speed'))['delivery_speed__avg']
        recommend_count = reviews.filter(would_recommend=True).count()
        recommend_percentage = (recommend_count / total_reviews) * 100
    else:
        avg_rating = 0
        avg_quality = 0
        avg_communication = 0
        avg_delivery = 0
        recommend_percentage = 0
    
    context = {
        'farmer': farmer,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'avg_quality': avg_quality,
        'avg_communication': avg_communication,
        'avg_delivery': avg_delivery,
        'recommend_percentage': recommend_percentage,
    }
    # Template path updated
    return render(request, 'marketplace/reviews/farmer_reviews.html', context)


@login_required
def add_response(request, review_id):
    """
    Farmer responds to a review
    """
    review = get_object_or_404(Review, pk=review_id, farmer=request.user)
    
    # Check if response already exists
    if hasattr(review, 'response'):
        messages.error(request, 'You have already responded to this review!')
        # Redirect to marketplace:farmer_reviews
        return redirect('marketplace:farmer_reviews', farmer_id=request.user.id)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text')
        
        ReviewResponse.objects.create(
            review=review,
            response_text=response_text
        )
        
        messages.success(request, 'Response added successfully!')
        return redirect('marketplace:farmer_reviews', farmer_id=request.user.id)
    
    context = {
        'review': review
    }
    # Template path updated
    return render(request, 'marketplace/reviews/add_response.html', context)


def update_farmer_rating(farmer):
    """
    Update farmer's average rating in their profile
    """
    try:
        profile = farmer.farmer_profile
        reviews = Review.objects.filter(farmer=farmer)
        
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            total_sales = Order.objects.filter(farmer=farmer, status='completed').count()
            
            profile.rating_average = round(avg_rating, 2)
            profile.total_sales = total_sales
            profile.save()
    except FarmerProfile.DoesNotExist:
        pass
