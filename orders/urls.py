from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place/<int:product_id>/', views.place_order, name='place_order'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]