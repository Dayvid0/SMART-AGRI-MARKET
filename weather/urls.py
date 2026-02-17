from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    # Main Climate Suite Dashboard
    path('', views.climate_suite, name='climate_suite'),
    
    # API endpoint for the JavaScript auto-rotation data
    path('api/get-weather/', views.get_weather_api, name='get_weather_api'),
    
    # Pest Alert details
    path('pest/<int:pk>/', views.pest_alert_detail, name='pest_alert_detail'),
]