from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notifications_page(request):
    """Full notifications page"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read when visiting this page with the query param ?mark_all_read=1
    if request.GET.get('mark_all_read'):
        notifications.filter(read=False).update(read=True)
        return redirect('notifications:notifications_page')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(read=False).count(),
    }
    return render(request, 'notifications/notifications_page.html', context)

@login_required
def get_notifications(request):
    """API endpoint for the header notification dropdown"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    unread_count = Notification.objects.filter(user=request.user, read=False).count()
    
    data = {
        'notifications': [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'link': n.link,
                'read': n.read,
                'created_at': n.created_at.isoformat()
            }
            for n in notifications
        ],
        'unread_count': unread_count
    }
    return JsonResponse(data)

@login_required
def mark_as_read(request, notification_id):
    """API endpoint to mark a single notification as read via JavaScript"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return JsonResponse({'status': 'success'})