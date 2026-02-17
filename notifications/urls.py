# apps/notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('api/', views.get_notifications, name='get_notifications'),
    path('api/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('', views.notifications_page, name='notifications_page'),
]