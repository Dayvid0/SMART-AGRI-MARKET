from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db.models import Q
import json

from marketplace.models import Product
from .models import ChatThread, ChatMessage, NegotiatedDeal
from notifications.helpers import notify_new_chat_message, notify_chat_thread_closed


@login_required
def unread_count(request):
    """
    Lightweight AJAX endpoint for the navbar badge.
    Returns total unread messages across all of the user's threads.
    """
    count = ChatMessage.objects.filter(
        thread__in=ChatThread.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        ),
        is_read=False
    ).exclude(sender=request.user).count()
    return JsonResponse({'unread_count': count})


@login_required
def open_chat(request, product_id):
    """
    Called when a buyer clicks 'Negotiate Price' on a product.
    Finds or creates a thread for this buyer-product pair, then
    redirects to the chat room — mirroring the SafeBoda match-then-chat flow.
    """
    product = get_object_or_404(Product, pk=product_id)

    # Prevent seller from chatting with themselves
    if request.user == product.farmer:
        return redirect('marketplace:product_detail', pk=product_id)

    thread, created = ChatThread.objects.get_or_create(
        product=product,
        buyer=request.user,
        defaults={'seller': product.farmer}
    )

    return redirect('chat:chat_room', thread_id=thread.pk)


@login_required
def chat_room(request, thread_id):
    """
    The main chat UI — a WhatsApp-style interface tied to a product negotiation.
    Both buyer and seller can access; all others are blocked.
    """
    thread = get_object_or_404(ChatThread, pk=thread_id)

    # Security: only thread participants can view
    if request.user not in [thread.buyer, thread.seller]:
        return redirect('marketplace:home')

    # Mark all messages from the other party as read when entering the room
    thread.messages.exclude(sender=request.user).update(is_read=True)

    messages = thread.messages.select_related('sender').order_by('sent_at')

    context = {
        'thread': thread,
        'messages': messages,
        'product': thread.product,
        'other_user': thread.seller if request.user == thread.buyer else thread.buyer,
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
@require_POST
def send_message(request, thread_id):
    """
    AJAX endpoint: Buyer or seller submits a message.
    Returns JSON with the new message data.
    """
    thread = get_object_or_404(ChatThread, pk=thread_id)

    if request.user not in [thread.buyer, thread.seller]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
    except (json.JSONDecodeError, AttributeError):
        content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    message = ChatMessage.objects.create(
        thread=thread,
        sender=request.user,
        content=content
    )

    # Bump thread's updated_at
    thread.save(update_fields=['updated_at'])

    # Fire bell notification to the OTHER participant
    try:
        notify_new_chat_message(message)
    except Exception:
        pass

    return JsonResponse({
        'id': message.pk,
        'sender': message.sender.username,
        'sender_id': message.sender.pk,
        'content': message.content,
        'sent_at': message.sent_at.strftime('%b %d, %Y %H:%M'),
        'sent_at_time': message.sent_at.strftime('%H:%M'),
        'is_own': True,
    })


@login_required
@require_GET
def poll_messages(request, thread_id):
    """
    AJAX polling endpoint: Returns messages sent after a given message ID.
    Called every 3 seconds by the front-end to simulate real-time chat.
    """
    thread = get_object_or_404(ChatThread, pk=thread_id)

    if request.user not in [thread.buyer, thread.seller]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0

    new_messages = thread.messages.filter(pk__gt=last_id).select_related('sender')

    # Mark newly fetched messages as read if they're from the other party
    new_messages.exclude(sender=request.user).update(is_read=True)

    data = []
    for msg in new_messages:
        data.append({
            'id': msg.pk,
            'sender': msg.sender.username,
            'sender_id': msg.sender.pk,
            'content': msg.content,
            'msg_type': msg.msg_type,
            'offer_price': float(msg.offer_price) if msg.offer_price else None,
            'offer_quantity': msg.offer_quantity,
            'offer_status': msg.offer_status,
            'deal_id': getattr(msg, 'deal', None).pk if hasattr(msg, 'deal') else None,
            'sent_at': msg.sent_at.strftime('%b %d, %Y %H:%M'),
            'sent_at_time': msg.sent_at.strftime('%H:%M'),
            'is_own': msg.sender == request.user,
        })

    return JsonResponse({
        'messages': data,
        'thread_status': thread.status,
    })


@login_required
def my_chats(request):
    """
    Inbox view — lists all negotiation threads for the current user (as buyer or seller).
    """
    threads = ChatThread.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('product', 'buyer', 'seller', 'product__farmer').order_by('-updated_at')

    # Annotate each thread with unread count for current user
    threads_with_data = []
    for thread in threads:
        last_msg = thread.get_last_message()
        unread = thread.get_unread_count(request.user)
        other = thread.seller if request.user == thread.buyer else thread.buyer
        threads_with_data.append({
            'thread': thread,
            'last_message': last_msg,
            'unread_count': unread,
            'other_user': other,
        })

    context = {
        'threads_with_data': threads_with_data,
        'total_unread': sum(t['unread_count'] for t in threads_with_data),
    }
    return render(request, 'chat/my_chats.html', context)


@login_required
@require_POST
def close_thread(request, thread_id):
    """
    Allows seller or admin to close a negotiation thread.
    """
    thread = get_object_or_404(ChatThread, pk=thread_id)

    if request.user not in [thread.buyer, thread.seller] and not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    thread.status = 'closed'
    thread.save(update_fields=['status', 'updated_at'])
    try:
        notify_chat_thread_closed(thread, closed_by=request.user)
    except Exception:
        pass
    return JsonResponse({'status': 'closed'})


@login_required
@require_POST
def reopen_thread(request, thread_id):
    """
    Allows seller to reopen a closed negotiation.
    """
    thread = get_object_or_404(ChatThread, pk=thread_id)

    if request.user not in [thread.buyer, thread.seller] and not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    thread.status = 'open'
    thread.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'status': 'open'})


@login_required
@require_POST
def send_offer(request, thread_id):
    """
    AJAX endpoint: Seller sends a formal price offer.
    """
    thread = get_object_or_404(ChatThread, pk=thread_id)
    if request.user != thread.seller:
        return JsonResponse({'error': 'Only the seller can make offers.'}, status=403)
    
    try:
        data = json.loads(request.body)
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid data provided.'}, status=400)
    
    if price <= 0 or quantity <= 0:
        return JsonResponse({'error': 'Price and quantity must be greater than zero.'}, status=400)
    
    # Mark any previous pending offers as superseded
    thread.messages.filter(msg_type='offer', offer_status='pending').update(offer_status='superseded')
    
    message = ChatMessage.objects.create(
        thread=thread,
        sender=request.user,
        content=f"I can offer you {quantity} {thread.product.unit} at UGX {price:,.0f} each.",
        msg_type='offer',
        offer_price=price,
        offer_quantity=quantity,
        offer_status='pending'
    )
    
    thread.save(update_fields=['updated_at'])
    
    try:
        notify_new_chat_message(message)
    except Exception:
        pass
    
    return JsonResponse({
        'id': message.pk,
        'sender': message.sender.username,
        'sender_id': message.sender.pk,
        'content': message.content,
        'msg_type': message.msg_type,
        'offer_price': float(message.offer_price),
        'offer_quantity': message.offer_quantity,
        'offer_status': message.offer_status,
        'sent_at': message.sent_at.strftime('%b %d, %Y %H:%M'),
        'sent_at_time': message.sent_at.strftime('%H:%M'),
        'is_own': True,
    })


@login_required
@require_POST
def respond_offer(request, message_id):
    """
    AJAX endpoint: Buyer accepts or rejects an offer.
    """
    message = get_object_or_404(ChatMessage, pk=message_id, msg_type='offer', offer_status='pending')
    thread = message.thread
    
    if request.user != message.thread.buyer:
        return JsonResponse({'error': 'Only the buyer can respond to offers.'}, status=403)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data.'}, status=400)
    
    if action == 'accept':
        message.offer_status = 'accepted'
        message.save(update_fields=['offer_status'])
        
        deal = NegotiatedDeal.objects.create(
            thread=thread,
            offer_message=message,
            agreed_price=message.offer_price,
            agreed_quantity=message.offer_quantity
        )
        
        # Send system message confirming deal
        ChatMessage.objects.create(
            thread=thread,
            sender=request.user,
            content=f"Deal accepted: {deal.agreed_quantity} {thread.product.unit} at UGX {deal.agreed_price:,.0f} each.",
            msg_type='offer_accepted'
        )
        
        thread.save(update_fields=['updated_at'])
        
        return JsonResponse({
            'status': 'accepted',
            'deal_id': deal.pk
        })
        
    elif action == 'reject':
        message.offer_status = 'rejected'
        message.save(update_fields=['offer_status'])
        
        ChatMessage.objects.create(
            thread=thread,
            sender=request.user,
            content="I have rejected the offer.",
            msg_type='offer_rejected'
        )
        
        thread.save(update_fields=['updated_at'])
        
        return JsonResponse({'status': 'rejected'})
        
    return JsonResponse({'error': 'Invalid action.'}, status=400)
