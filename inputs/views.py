from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import AgriculturalInput, InputCategory, GroupBuyPool, GroupBuyParticipant


def input_store(request):
    """
    Main input store listing page
    """
    inputs = AgriculturalInput.objects.filter(status='available').select_related('category', 'supplier')

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
    ).select_related('input_item', 'organizer')[:4]

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
        try:
            target_quantity = int(request.POST.get('target_quantity', 0))
            my_quantity = int(request.POST.get('my_quantity', 0))
            deadline = request.POST.get('deadline')

            if target_quantity <= 0 or my_quantity <= 0:
                messages.error(request, 'Quantities must be greater than zero.')
                return render(request, 'inputs/create_group_buy.html', {'input_item': input_item})

            if my_quantity > target_quantity:
                messages.error(request, 'Your quantity cannot exceed the target quantity.')
                return render(request, 'inputs/create_group_buy.html', {'input_item': input_item})

            if not deadline:
                messages.error(request, 'Please set a deadline for the pool.')
                return render(request, 'inputs/create_group_buy.html', {'input_item': input_item})

            deadline_dt = parse_datetime(deadline)
            if deadline_dt is None:
                messages.error(request, 'Invalid deadline format.')
                return render(request, 'inputs/create_group_buy.html', {'input_item': input_item})
            if timezone.is_naive(deadline_dt):
                deadline_dt = timezone.make_aware(deadline_dt)
            if deadline_dt <= timezone.now():
                messages.error(request, 'Deadline must be set in the future.')
                return render(request, 'inputs/create_group_buy.html', {'input_item': input_item})

            # Create pool
            pool = GroupBuyPool.objects.create(
                input_item=input_item,
                organizer=request.user,
                target_quantity=target_quantity,
                current_quantity=my_quantity,
                deadline=deadline_dt,
                status='open'
            )

            # Add organizer as first participant
            GroupBuyParticipant.objects.create(
                pool=pool,
                farmer=request.user,
                quantity=my_quantity
            )

            messages.success(request, 'Group buy pool created! Share with other farmers to reach the target.')
            return redirect('inputs:group_buy_detail', pool_id=pool.id)

        except (ValueError, TypeError):
            messages.error(request, 'Invalid input. Please check the quantities and try again.')

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
    participants = pool.participants.select_related('farmer').all()

    # Check if user already joined
    user_participation = participants.filter(farmer=request.user).first()

    # Calculate progress
    progress_percentage = min(
        (pool.current_quantity / pool.target_quantity * 100) if pool.target_quantity > 0 else 0,
        100
    )

    # Calculate discounted group price
    discount = pool.input_item.group_discount_percentage
    regular_price = pool.input_item.price
    group_price = regular_price * (1 - discount / 100) if discount > 0 else regular_price

    # Check if deadline has passed but pool is still 'open'
    if pool.status == 'open' and pool.deadline < timezone.now():
        pool.status = 'cancelled'
        pool.save()

    context = {
        'pool': pool,
        'participants': participants,
        'user_participation': user_participation,
        'progress_percentage': progress_percentage,
        'group_price': group_price,
        'remaining': max(pool.target_quantity - pool.current_quantity, 0),
    }

    return render(request, 'inputs/group_buy_detail.html', context)


@login_required
def join_group_buy(request, pool_id):
    """
    Join an existing group buy pool
    """
    pool = get_object_or_404(GroupBuyPool, pk=pool_id)

    # Check pool is still open
    if pool.status != 'open' or pool.deadline < timezone.now():
        messages.error(request, 'This group buy pool is no longer accepting participants.')
        return redirect('inputs:group_buy_detail', pool_id=pool.id)

    # Check if already joined
    if pool.participants.filter(farmer=request.user).exists():
        messages.error(request, 'You have already joined this group buy!')
        return redirect('inputs:group_buy_detail', pool_id=pool.id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 0))
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than zero.')
                return render(request, 'inputs/join_group_buy.html', {'pool': pool})

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
                messages.success(request, f'🎉 Target reached! The group buy is now closed and the order will be placed.')
            else:
                messages.success(request, f'Successfully joined group buy! Added {quantity} {pool.input_item.unit}.')

            pool.save()
            return redirect('inputs:group_buy_detail', pool_id=pool.id)

        except (ValueError, TypeError):
            messages.error(request, 'Invalid quantity. Please enter a valid number.')

    context = {
        'pool': pool
    }
    return render(request, 'inputs/join_group_buy.html', context)


@login_required
def leave_group_buy(request, pool_id):
    """
    Leave an existing group buy pool (non-organizer only)
    """
    pool = get_object_or_404(GroupBuyPool, pk=pool_id)

    if pool.organizer == request.user:
        messages.error(request, 'As the organizer, you cannot leave. You can cancel the pool instead.')
        return redirect('inputs:group_buy_detail', pool_id=pool.id)

    participation = get_object_or_404(GroupBuyParticipant, pool=pool, farmer=request.user)

    if pool.status != 'open':
        messages.error(request, 'You cannot leave a pool that is no longer open.')
        return redirect('inputs:group_buy_detail', pool_id=pool.id)

    if request.method == 'POST':
        # Restore quantity to pool
        pool.current_quantity -= participation.quantity
        if pool.current_quantity < 0:
            pool.current_quantity = 0
        pool.save()

        participation.delete()
        messages.success(request, 'You have left the group buy pool.')
        return redirect('inputs:group_buy_list')

    context = {'pool': pool, 'participation': participation}
    return render(request, 'inputs/leave_group_buy_confirm.html', context)


@login_required
def cancel_group_buy(request, pool_id):
    """
    Cancel a group buy pool (organizer only)
    """
    pool = get_object_or_404(GroupBuyPool, pk=pool_id)

    if pool.organizer != request.user:
        messages.error(request, 'Only the organizer can cancel this pool.')
        return redirect('inputs:group_buy_detail', pool_id=pool.id)

    if pool.status not in ('open',):
        messages.error(request, 'Only open pools can be cancelled.')
        return redirect('inputs:group_buy_detail', pool_id=pool.id)

    if request.method == 'POST':
        pool.status = 'cancelled'
        pool.save()
        messages.success(request, 'Group buy pool has been cancelled.')
        return redirect('inputs:my_pools')

    context = {'pool': pool}
    return render(request, 'inputs/cancel_group_buy_confirm.html', context)


@login_required
def my_pools(request):
    """
    Show user's group buy pools — organized and joined
    """
    organized = GroupBuyPool.objects.filter(
        organizer=request.user
    ).select_related('input_item').order_by('-created_at')

    joined = GroupBuyParticipant.objects.filter(
        farmer=request.user
    ).exclude(
        pool__organizer=request.user
    ).select_related('pool', 'pool__input_item').order_by('-joined_at')

    context = {
        'organized_pools': organized,
        'joined_pools': joined,
    }
    return render(request, 'inputs/my_pools.html', context)


def group_buy_list(request):
    """
    List all active group buy pools
    """
    status_filter = request.GET.get('status', 'open')

    pools = GroupBuyPool.objects.select_related('input_item', 'organizer')

    if status_filter == 'open':
        pools = pools.filter(status='open', deadline__gte=timezone.now())
    elif status_filter == 'closed':
        pools = pools.filter(status='closed')
    elif status_filter == 'all':
        pools = pools.all()
    else:
        pools = pools.filter(status='open', deadline__gte=timezone.now())

    pools = pools.order_by('-created_at')

    context = {
        'pools': pools,
        'status_filter': status_filter,
    }

    return render(request, 'inputs/group_buy_list.html', context)