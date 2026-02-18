from django.urls import path
from . import views
app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('market-prices/', views.market_prices, name='market_prices'),
    path('price-tracker/', views.price_tracker, name='price_tracker'),
    path('districts/', views.district_list, name='district_list'),
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('report-price/', views.report_price, name='report_price'),
    
    # Reviews
    path('reviews/create/<int:order_id>/', views.create_review, name='create_review'),
    path('reviews/farmer/<int:farmer_id>/', views.farmer_reviews, name='farmer_reviews'),
    path('reviews/response/<int:review_id>/', views.add_response, name='add_response'),
]