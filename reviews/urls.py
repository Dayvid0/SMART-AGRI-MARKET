from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:order_id>/', views.create_review, name='create_review'),
    path('farmer/<int:farmer_id>/', views.farmer_reviews, name='farmer_reviews'),
    path('response/<int:review_id>/', views.add_response, name='add_response'),
]