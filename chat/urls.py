from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Buyer opens / resumes chat about a product
    path('start/<int:product_id>/', views.open_chat, name='open_chat'),

    # The actual chat room
    path('room/<int:thread_id>/', views.chat_room, name='chat_room'),

    # AJAX: send a message
    path('send/<int:thread_id>/', views.send_message, name='send_message'),

    # AJAX: poll for new messages
    path('poll/<int:thread_id>/', views.poll_messages, name='poll_messages'),

    # AJAX: unread count for navbar badge
    path('unread-count/', views.unread_count, name='unread_count'),

    # Inbox: all threads for the logged-in user
    path('inbox/', views.my_chats, name='my_chats'),

    # Thread management
    path('close/<int:thread_id>/', views.close_thread, name='close_thread'),
    path('reopen/<int:thread_id>/', views.reopen_thread, name='reopen_thread'),

    # Offers
    path('offer/<int:thread_id>/', views.send_offer, name='send_offer'),
    path('offer-respond/<int:message_id>/', views.respond_offer, name='respond_offer'),
]
