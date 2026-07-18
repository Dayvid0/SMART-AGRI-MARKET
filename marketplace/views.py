import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Max, Min, Count
from datetime import date, timedelta
from django.db.models import Count

from .models import Product, Category, MarketPrice, CrowdsourcedPrice, ExternalMarketPrice
from orders.models import Order
from accounts.models import FarmerProfile
from accounts.constants import UGANDA_REGIONS, DISTRICT_COORDINATES
from .services.price_fetcher import combine_price_sources

# --- MARKETPLACE VIEWS ---

def home(request):
    """
    Homepage view - displays featured products, categories, news, weather, and user data
    """
    if not request.user.is_authenticated:
        return render(request, 'marketplace/landing.html')
        
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

    # Latest 3 published news articles
    try:
        from news.models import AgriNews
        latest_news = (
            AgriNews.objects
            .filter(status='published')
            .order_by('-published_at')[:3]
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
            recent_orders = (
                Order.objects
                .filter(buyer=request.user)
                .order_by('-created_at')[:3]
            )
        except Exception:
            try:
                recent_orders = (
                    Order.objects
                    .filter(farmer=request.user)
                    .order_by('-created_at')[:3]
                )
            except Exception:
                recent_orders = []

    # Top real reviews for testimonials section (4+ stars, most recent)
    try:
        from .models import Review
        top_reviews = list(
            Review.objects
            .filter(rating__gte=4)
            .select_related('reviewer', 'farmer')
            .order_by('-rating', '-created_at')[:3]
        )
    except Exception:
        top_reviews = []

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
        'hybrid_prices':        hybrid_prices,
        'all_districts':        UGANDA_REGIONS,
        'top_reviews':          top_reviews,
    }
    return render(request, 'marketplace/home.html', context)


def product_list(request):
    """
    Display all products with search and filter functionality
    """
    from django.core.paginator import Paginator

    products = Product.objects.filter(status='available').select_related('farmer', 'farmer__farmer_profile', 'category')
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    location = request.GET.get('location')
    urgent_only = request.GET.get('urgent')
    sort = request.GET.get('sort', '-created_at')

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

    # Sorting
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        '-created_at': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    urgent_products = Product.objects.filter(status='available', is_urgent=True)[:4]
    categories = Category.objects.all()
    locations = Product.objects.values_list('location', flat=True).distinct()

    # Pagination — 12 per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,          # now a page object
        'page_obj': page_obj,
        'categories': categories,
        'locations': locations,
        'selected_category': category_id,
        'search_query': search_query,
        'selected_location': location,
        'urgent_products': urgent_products,
        'urgent_only': urgent_only,
        'sort': sort,
    }
    return render(request, 'marketplace/product_list.html', context)



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status='available')
    related_products = Product.objects.filter(category=product.category, status='available').exclude(pk=pk)[:4]
    return render(request, 'marketplace/product_detail.html', {'product': product, 'related_products': related_products})


# --- PRICE INTELLIGENCE VIEWS ---

def market_prices(request):
    """
    Unified price intelligence — combines WFP/HDX external prices,
    farmer-crowdsourced prices, and admin-entered official prices.
    """
    month_ago = date.today() - timedelta(days=30)
    product_filter = request.GET.get('product', '').strip().lower()

    # 1. External prices (WFP / HDX) — aggregated per product
    ext_qs = ExternalMarketPrice.objects.filter(is_active=True, date_recorded__gte=month_ago)
    external_summary = (
        ext_qs.values('product_name', 'unit')
        .annotate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            data_points=Count('id'),
            latest_date=Max('date_recorded'),
        )
        .order_by('product_name')
    )

    # 2. Crowdsourced prices — aggregated per product
    cs_summary = (
        CrowdsourcedPrice.objects
        .filter(date_reported__gte=month_ago)
        .values('product_name', 'unit')
        .annotate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            report_count=Count('id'),
        )
        .order_by('product_name')
    )

    # 3. Official/manual prices — aggregated per product
    official_summary = (
        MarketPrice.objects
        .filter(date_recorded__gte=month_ago)
        .values('product_name', 'unit')
        .annotate(
            avg_price=Avg('average_price'),
            min_price=Avg('min_price'),
            max_price=Avg('max_price'),
        )
        .order_by('product_name')
    )

    # Build lookup maps keyed by normalised product name
    ext_map = {r['product_name'].lower(): r for r in external_summary}
    cs_map  = {r['product_name'].lower(): r for r in cs_summary}
    off_map = {r['product_name'].lower(): r for r in official_summary}

    all_keys = sorted(set(ext_map) | set(cs_map) | set(off_map))

    # Apply optional product filter
    if product_filter:
        all_keys = [k for k in all_keys if product_filter in k]

    unified_prices = []
    for key in all_keys:
        ext = ext_map.get(key)
        cs  = cs_map.get(key)
        off = off_map.get(key)
        first = ext or cs or off
        unified_prices.append({
            'product_name': first['product_name'],
            'unit': first['unit'],
            'external': ext,
            'crowdsourced': cs,
            'official': off,
        })

    last_fetch = (
        ExternalMarketPrice.objects
        .filter(is_active=True)
        .order_by('-fetched_at')
        .values_list('fetched_at', flat=True)
        .first()
    )

    context = {
        'unified_prices': unified_prices,
        'product_filter': product_filter,
        'last_fetch': last_fetch,
        'ext_count': len(ext_map),
        'cs_count': len(cs_map),
        'off_count': len(off_map),
    }
    return render(request, 'marketplace/market_prices.html', context)


@login_required
def report_price(request):
    """
    Farmers report prices they're actually getting in the field.
    """
    if request.method == 'POST':
        product_name = request.POST.get('product_name', '').strip()
        price_raw    = request.POST.get('price', '').strip()
        unit         = request.POST.get('unit', '').strip()
        buyer_type   = request.POST.get('buyer_type', '').strip()
        location     = request.POST.get('location', '').strip()

        error = None
        if not product_name:
            error = 'Product name is required.'
        elif not price_raw:
            error = 'Price is required.'
        elif not unit:
            error = 'Please select a unit.'
        elif not buyer_type:
            error = 'Please select a buyer type.'
        elif not location:
            error = 'Location is required.'
        else:
            try:
                price_val = float(price_raw)
                if price_val <= 0:
                    raise ValueError
            except ValueError:
                error = 'Please enter a valid price greater than zero.'

        if error:
            messages.error(request, error)
        else:
            CrowdsourcedPrice.objects.create(
                reporter=request.user,
                product_name=product_name,
                price=price_val,
                unit=unit,
                buyer_type=buyer_type,
                location=location,
                market_name=request.POST.get('market_name', '').strip(),
                notes=request.POST.get('notes', '').strip(),
            )
            messages.success(request, 'Thank you! Your price report helps other farmers.')
            return redirect('marketplace:price_tracker')

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


# --- TRANSPORTER VIEWS ---

@login_required
def transporter_dashboard(request):
    """
    Dashboard for transporters to view open delivery requests
    and manage their assigned deliveries.
    """
    if request.user.user_type != 'transporter':
        messages.error(request, 'Only transporters can access this dashboard.')
        return redirect('home')
        
    from orders.models import DeliveryRequest
    
    # Optional: Filter by transporter's districts
    # TransporterProfile should exist if registered as transporter
    # tp = getattr(request.user, 'transporter_profile', None)
    # districts = tp.get_districts_list() if tp else []
    
    # Open requests looking for transporters
    open_requests = DeliveryRequest.objects.filter(status='open').select_related('order', 'order__farmer')
    
    # My active/past deliveries
    my_deliveries = DeliveryRequest.objects.filter(
        transporter=request.user
    ).exclude(status='open').select_related('order', 'order__buyer', 'order__farmer').order_by('-created_at')
    
    # Quick Stats
    active_count = my_deliveries.filter(status__in=['assigned', 'in_transit']).count()
    completed_count = my_deliveries.filter(status='delivered').count()
    
    # Sum earnings
    from django.db.models import Sum
    earnings = my_deliveries.filter(status='delivered').aggregate(total=Sum('offered_price'))['total'] or 0
    
    context = {
        'open_requests': open_requests,
        'my_deliveries': my_deliveries,
        'active_count': active_count,
        'completed_count': completed_count,
        'earnings': earnings,
    }
    return render(request, 'marketplace/transporter_dashboard.html', context)


# --- FARMER MANAGEMENT VIEWS ---

@login_required
def farmer_dashboard(request):
    # Allow both farmers and business users to manage their listings
    if request.user.user_type not in ('farmer', 'business'):
        messages.error(request, 'Only farmers and business accounts can access the seller dashboard!')
        return redirect('marketplace:home')
    
    products = Product.objects.filter(farmer=request.user)
    orders_received = Order.objects.filter(farmer=request.user).order_by('-created_at')[:5]
    
    farmer_profile = getattr(request.user, 'farmer_profile', None)
    total_sales = farmer_profile.total_sales if farmer_profile else 0

    context = {
        'products': products,
        'orders_received': orders_received,
        'total_products': products.count(),
        'available_products': products.filter(status='available').count(),
        'pending_orders': Order.objects.filter(farmer=request.user, status='pending').count(),
        'farmer_profile': farmer_profile,
        'total_sales': total_sales,
    }
    return render(request, 'marketplace/farmer_dashboard.html', context)


@login_required
def add_product(request):
    """Allow farmers and business users to list a new product for sale."""
    # Permission check
    if request.user.user_type not in ('farmer', 'business'):
        messages.error(request, 'Only farmers and business accounts can add products.')
        return redirect('marketplace:home')

    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        # ── Collect POST values ──────────────────────────────
        name            = request.POST.get('name', '').strip()
        category_id     = request.POST.get('category', '').strip()
        description     = request.POST.get('description', '').strip()
        price_raw       = request.POST.get('price', '').strip()
        quantity_raw    = request.POST.get('quantity', '').strip()
        unit            = request.POST.get('unit', 'kg').strip()
        location        = request.POST.get('location', '').strip()
        harvest_date    = request.POST.get('harvest_date', '').strip() or None
        is_urgent       = request.POST.get('is_urgent') == 'on'
        urgent_discount = request.POST.get('urgent_discount', '0').strip() or '0'

        # ── Validation ───────────────────────────────────────
        errors = []

        if not name:
            errors.append('Product name is required.')
        if not category_id:
            errors.append('Please select a category.')
        if not description:
            errors.append('Product description is required.')
        if not location:
            errors.append('Location / district is required.')

        # Validate price
        try:
            price = float(price_raw)
            if price <= 0:
                errors.append('Price must be greater than zero.')
        except (ValueError, TypeError):
            price = None
            errors.append('Enter a valid price (numbers only).')

        # Validate quantity
        try:
            quantity = int(quantity_raw)
            if quantity <= 0:
                errors.append('Quantity must be at least 1.')
        except (ValueError, TypeError):
            quantity = None
            errors.append('Enter a valid quantity (whole number).')

        # Validate category exists
        category_obj = None
        if category_id:
            try:
                category_obj = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                errors.append('Selected category does not exist.')

        # Validate urgent discount
        try:
            urgent_discount_val = int(urgent_discount)
            if urgent_discount_val < 0 or urgent_discount_val > 50:
                urgent_discount_val = 0
        except (ValueError, TypeError):
            urgent_discount_val = 0

        if errors:
            for err in errors:
                messages.error(request, err)
            # Re-render form with submitted values preserved
            return render(request, 'marketplace/add_product.html', {
                'categories': categories,
                'form_data': request.POST,   # template can reuse these
            })

        # ── Save ─────────────────────────────────────────────
        try:
            product = Product.objects.create(
                farmer          = request.user,
                category        = category_obj,
                name            = name,
                description     = description,
                price           = price,
                quantity        = quantity,
                unit            = unit,
                location        = location,
                image           = request.FILES.get('image') or None,
                image2          = request.FILES.get('image2') or None,
                image3          = request.FILES.get('image3') or None,
                is_urgent       = is_urgent,
                urgent_discount = urgent_discount_val,
                harvest_date    = harvest_date if harvest_date else None,
                status          = 'available',
            )
            messages.success(request, f'✅ Product "{product.name}" listed successfully! Buyers can now see it.')
            return redirect('marketplace:farmer_dashboard')

        except Exception as e:
            messages.error(request, f'Something went wrong while saving your product. Please try again. ({e})')
            return render(request, 'marketplace/add_product.html', {
                'categories': categories,
                'form_data': request.POST,
            })

    # ── GET ───────────────────────────────────────────────────
    return render(request, 'marketplace/add_product.html', {
        'categories': categories,
        'form_data': {},
    })


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
        return redirect('marketplace:farmer_dashboard')
    
    return render(request, 'marketplace/edit_product.html', {'product': product, 'categories': Category.objects.all()})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted!')
        return redirect('marketplace:farmer_dashboard')
    return render(request, 'marketplace/delete_product.html', {'product': product})


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
        'mapbox_token': os.environ.get('MAPBOX_TOKEN', '')
    }
    return render(request, 'marketplace/district_list.html', context)

def farmer_list(request):
    """
    Display a list of all registered farmers grouped by region.
    Supports search (name/district), region filter, and crop filter.
    """
    from accounts.models import User

    # Farmers should not see a directory of other farmers
    if request.user.is_authenticated and request.user.user_type == 'farmer':
        messages.info(request, 'The Farmer Directory is for buyers and businesses. You can manage your own listings from your dashboard.')
        return redirect('marketplace:farmer_dashboard')

    # Use imported regions
    REGIONS = UGANDA_REGIONS

    # ── Filter parameters ──
    search_query   = request.GET.get('search', '').strip()
    region_filter  = request.GET.get('region', '').strip()
    crop_filter    = request.GET.get('crop', '').strip()
    rating_filter  = request.GET.get('rating', '').strip()

    farmers_qs = User.objects.filter(user_type='farmer').select_related('farmer_profile')

    # Search by username, district, or farm name
    if search_query:
        from django.db.models import Q
        farmers_qs = farmers_qs.filter(
            Q(username__icontains=search_query) |
            Q(district__icontains=search_query) |
            Q(farmer_profile__farm_name__icontains=search_query) |
            Q(farmer_profile__specialization__icontains=search_query)
        )

    # Rating filter (minimum average)
    if rating_filter:
        try:
            min_rating = float(rating_filter)
            farmers_qs = farmers_qs.filter(farmer_profile__rating_average__gte=min_rating)
        except ValueError:
            pass

    # Crop filter
    if crop_filter:
        farmers_qs = farmers_qs.filter(farmer_profile__specialization__icontains=crop_filter)

    # Group into regions (respecting optional region filter)
    farmers_by_region = {}
    for region in (REGIONS.keys() if not region_filter else [region_filter]):
        farmers_by_region[region] = []
    if not region_filter:
        farmers_by_region['Other'] = []

    for farmer in farmers_qs:
        district = farmer.district
        placed   = False
        if district:
            for region, districts in REGIONS.items():
                if district in districts:
                    if region_filter and region != region_filter:
                        placed = True  # skip — filtered out
                        break
                    farmers_by_region.setdefault(region, []).append(farmer)
                    placed = True
                    break
        if not placed and not region_filter:
            farmers_by_region.setdefault('Other', []).append(farmer)

    # Remove empty regions
    farmers_by_region = {k: v for k, v in farmers_by_region.items() if v}

    # Build distinct crop list for dropdown
    from accounts.models import FarmerProfile
    crop_list = (
        FarmerProfile.objects
        .exclude(specialization='')
        .exclude(specialization__isnull=True)
        .values_list('specialization', flat=True)
        .distinct()
        .order_by('specialization')
    )

    total_farmers = sum(len(v) for v in farmers_by_region.values())

    context = {
        'farmers_by_region': farmers_by_region,
        'region_list':  list(REGIONS.keys()),
        'crop_list':    list(crop_list),
        'search_query': search_query,
        'region_filter': region_filter,
        'crop_filter':  crop_filter,
        'rating_filter': rating_filter,
        'total_farmers': total_farmers,
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

        # Notify farmer about the new review
        try:
            from notifications.helpers import notify_new_review
            notify_new_review(review)
        except Exception:
            pass
        
        messages.success(request, 'Review submitted successfully!')
        return redirect('orders:order_detail', order_id=order_id)
    
    context = {
        'order': order
    }
    # Template path updated to marketplace/reviews
    return render(request, 'marketplace/reviews/create_review.html', context)


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
