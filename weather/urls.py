from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.climate_suite, name='climate_suite'),
    path('pest/<int:pk>/', views.pest_alert_detail, name='pest_alert_detail'),
]