from django.urls import path
from . import views
app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('market-prices/', views.market_prices, name='market_prices'),
    path('price-tracker/', views.price_tracker, name='price_tracker'),
    path('report-price/', views.report_price, name='report_price'),
]