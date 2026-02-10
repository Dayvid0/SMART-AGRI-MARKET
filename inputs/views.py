from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from .models import AgriculturalInput, InputCategory, GroupBuyPool, GroupBuyParticipant

def input_store(request):
    """
    Main input store listing page
    """
    inputs = AgriculturalInput.objects.filter(status='available')
    
    # Filters
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category_id:
        inputs = inputs.filter(category_id=category_id)
    
    if search_query:
        inputs = inputs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    categories = InputCategory.objects.all()
    
    # Active group buy pools
    active_pools = GroupBuyPool.objects.filter(
        status='open',
        deadline__gte=timezone.now()
    )[:4]
    
    context = {
        'inputs': inputs,
        'categories': categories,
        'active_pools': active_pools,
        'selected_category': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'inputs/input_store.html', context)


def input_detail(request, pk):
    """
    Input item detail page
    """
    input_item = get_object_or_404(AgriculturalInput, pk=pk)
    
    # Related inputs
    related_inputs = AgriculturalInput.objects.filter(
        category=input_item.category,
        status='available'
    ).exclude(pk=pk)[:4]
    
    # Active group buy pools for this item
    active_pools = GroupBuyPool.objects.filter(
        input_item=input_item,
        status='open',
        deadline__gte=timezone.now()
    )
    
    context = {
        'input_item': input_item,
        'related_inputs': related_inputs,
        'active_pools': active_pools,
    }
    
    return render(request, 'inputs/input_detail.html', context)


@login_required
def create_group_buy(request, input_id):
    """
    Create a group buy pool
    """
    input_item = get_object_or_404(AgriculturalInput, pk=input_id)
    
    if request.method == 'POST':
        target_quantity = int(request.POST.get('target_quantity'))
        my_quantity = int(request.POST.get('my_quantity'))
        deadline = request.POST.get('deadline')
        
        # Create pool
        pool = GroupBuyPool.objects.create(
            input_item=input_item,
            organizer=request.user,
            target_quantity=target_quantity,
            current_quantity=my_quantity,
            deadline=deadline,
            status='open'
        )
        
        # Add organizer as first participant
        GroupBuyParticipant.objects.create(
            pool=pool,
            farmer=request.user,
            quantity=my_quantity
        )
        
        messages.success(request, 'Group buy pool created! Share with other farmers to reach the target.')
        return redirect('group_buy_detail', pool_id=pool.id)
    
    context = {
        'input_item': input_item
    }
    return render(request, 'inputs/create_group_buy.html', context)


@login_required
def group_buy_detail(request, pool_id):
    """
    Group buy pool detail and join page
    """
    pool = get_object_or_404(GroupBuyPool, pk=pool_id)
    participants = pool.participants.all()
    
    # Check if user already joined
    user_participation = participants.filter(farmer=request.user).first()
    
    # Calculate progress
    progress_percentage = (pool.current_quantity / pool.target_quantity * 100) if pool.target_quantity > 0 else 0
    
    context = {
        'pool': pool,
        'participants': participants,
        'user_participation': user_participation,
        'progress_percentage': progress_percentage,
    }
    
    return render(request, 'inputs/group_buy_detail.html', context)


@login_required
def join_group_buy(request, pool_id):
    """
    Join an existing group buy pool
    """
    pool = get_object_or_404(GroupBuyPool, pk=pool_id)
    
    # Check if already joined
    if pool.participants.filter(farmer=request.user).exists():
        messages.error(request, 'You have already joined this group buy!')
        return redirect('group_buy_detail', pool_id=pool.id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        
        # Add participant
        GroupBuyParticipant.objects.create(
            pool=pool,
            farmer=request.user,
            quantity=quantity
        )
        
        # Update pool quantity
        pool.current_quantity += quantity
        
        # Check if target reached
        if pool.current_quantity >= pool.target_quantity:
            pool.status = 'closed'
        
        pool.save()
        
        messages.success(request, f'Successfully joined group buy! {quantity} units added.')
        return redirect('group_buy_detail', pool_id=pool.id)
    
    context = {
        'pool': pool
    }
    return render(request, 'inputs/join_group_buy.html', context)


def group_buy_list(request):
    """
    List all active group buy pools
    """
    active_pools = GroupBuyPool.objects.filter(
        status='open',
        deadline__gte=timezone.now()
    ).select_related('input_item', 'organizer')
    
    context = {
        'pools': active_pools
    }
    
    return render(request, 'inputs/group_buy_list.html', context)