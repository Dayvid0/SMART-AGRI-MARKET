from django.urls import path
from . import views

app_name = 'adminportal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('verifications/', views.verification_queue, name='verification_queue'),
    path('verifications/<int:vr_id>/approve/', views.approve_verification, name='approve_verification'),
    path('verifications/<int:vr_id>/reject/', views.reject_verification, name='reject_verification'),
    path('orders/', views.order_overview, name='order_overview'),
]
