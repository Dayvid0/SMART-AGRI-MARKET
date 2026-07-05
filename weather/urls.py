from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.climate_suite, name='climate_suite'),
    path('api/get-weather/', views.get_weather_api, name='get_weather_api'),
    path('api/recommendations/', views.get_recommendations_api, name='get_recommendations_api'),
    path('pest/<int:pk>/', views.pest_alert_detail, name='pest_alert_detail'),
]