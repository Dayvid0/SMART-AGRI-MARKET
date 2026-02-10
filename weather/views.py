from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import WeatherAlert, PlantingSeason, PestAlert
import requests
from datetime import datetime

def climate_suite(request):
    """
    Climate suite dashboard with weather, planting seasons, and pest alerts
    """
    # Active weather alerts
    active_alerts = WeatherAlert.objects.filter(
        is_active=True,
        end_date__gte=timezone.now()
    ).order_by('-severity')
    
    # Current planting seasons
    current_month = datetime.now().month
    planting_seasons = PlantingSeason.objects.all()[:6]
    
    # Active pest alerts
    pest_alerts = PestAlert.objects.filter(is_active=True)[:6]
    
    # Get weather for user's location (using OpenWeatherMap API)
    weather_data = None
    if request.user.is_authenticated and request.user.location:
        weather_data = get_weather_data(request.user.location)
    
    context = {
        'active_alerts': active_alerts,
        'planting_seasons': planting_seasons,
        'pest_alerts': pest_alerts,
        'weather_data': weather_data,
    }
    
    return render(request, 'weather/climate_suite.html', context)


def get_weather_data(location):
    """
    Fetch weather data from OpenWeatherMap API
    """
    API_KEY = 'be5fb80ee9e2e0af2f0292ec2d628012'  # Get free key from openweathermap.org
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    
    try:
        params = {
            'q': location + ',UG',  # Uganda
            'appid': API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(BASE_URL, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
            }
    except Exception as e:
        print(f"Weather API Error: {e}")
    
    return None


def pest_alert_detail(request, pk):
    """
    Detailed pest alert information
    """
    pest_alert = get_object_or_404(PestAlert, pk=pk)
    
    context = {
        'pest_alert': pest_alert
    }
    
    return render(request, 'weather/pest_alert_detail.html', context)