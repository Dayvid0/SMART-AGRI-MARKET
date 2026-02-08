from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Review, ReviewResponse
from orders.models import Order
from accounts.models import FarmerProfile

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
    if hasattr(order, 'review'):
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
    return render(request, 'reviews/create_review.html', context)


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
    return render(request, 'reviews/farmer_reviews.html', context)


@login_required
def add_response(request, review_id):
    """
    Farmer responds to a review
    """
    review = get_object_or_404(Review, pk=review_id, farmer=request.user)
    
    # Check if response already exists
    if hasattr(review, 'response'):
        messages.error(request, 'You have already responded to this review!')
        return redirect('reviews:farmer_reviews', farmer_id=request.user.id)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text')
        
        ReviewResponse.objects.create(
            review=review,
            response_text=response_text
        )
        
        messages.success(request, 'Response added successfully!')
        return redirect('reviews:farmer_reviews', farmer_id=request.user.id)
    
    context = {
        'review': review
    }
    return render(request, 'reviews/add_response.html', context)


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
    