from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place/<int:product_id>/', views.place_order, name='place_order'),
    path('place/input/<int:input_id>/', views.place_order, name='place_order_input'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('confirm-receipt/<int:order_id>/', views.confirm_receipt, name='confirm_receipt'),
    # Delivery routes
    path('delivery/request/<int:order_id>/', views.request_delivery, name='request_delivery'),
    path('delivery/<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
    path('delivery/accept/<int:delivery_id>/', views.accept_delivery, name='accept_delivery'),
    path('delivery/update-status/<int:delivery_id>/', views.update_delivery_status, name='update_delivery_status'),
    # Fallback for old notifications
    path('<int:order_id>/', views.order_detail, name='order_detail_legacy'),
]