from django.urls import path
from . import views

app_name = 'inputs'

urlpatterns = [
    path('', views.input_store, name='input_store'),
    path('detail/<int:pk>/', views.input_detail, name='input_detail'),
    path('group-buy/create/<int:input_id>/', views.create_group_buy, name='create_group_buy'),
    path('group-buy/<int:pool_id>/', views.group_buy_detail, name='group_buy_detail'),
    path('group-buy/join/<int:pool_id>/', views.join_group_buy, name='join_group_buy'),
    path('group-buy/list/', views.group_buy_list, name='group_buy_list'),
]