from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse # Added for the API
from .models import WeatherAlert, PlantingSeason, PestAlert
import requests
from datetime import datetime

def climate_suite(request):
    """
    Climate suite dashboard with weather, planting seasons, and pest alerts
    """
    active_alerts = WeatherAlert.objects.filter(
        is_active=True,
        end_date__gte=timezone.now()
    ).order_by('-severity')
    
    planting_seasons = PlantingSeason.objects.all()[:6]
    pest_alerts = PestAlert.objects.filter(is_active=True)[:6]
    
    # List of districts for the auto-rotating JavaScript dashboard
    featured_districts = ['Kampala', 'Entebbe', 'Mbarara', 'Gulu', 'Jinja', 'Mbale']
    
    # Get initial weather for user's location or default to Kampala
    user_location = request.user.location if request.user.is_authenticated and request.user.location else 'Kampala'
    weather_data = get_weather_data(user_location)
    
    context = {
        'active_alerts': active_alerts,
        'planting_seasons': planting_seasons,
        'pest_alerts': pest_alerts,
        'weather_data': weather_data,
        'featured_districts': featured_districts, # Added for JS
    }
    
    return render(request, 'weather/climate_suite.html', context)

def get_weather_api(request):
    """
    API endpoint for JavaScript to fetch weather for a specific district
    Usage: /weather/api/get-weather/?district=Gulu
    """
    district = request.GET.get('district', 'Kampala')
    data = get_weather_data(district)
    
    if data:
        return JsonResponse(data)
    return JsonResponse({'error': 'Could not fetch weather data'}, status=400)

def get_weather_data(location):
    """
    Fetch weather data from OpenWeatherMap API
    """
    API_KEY = 'be5fb80ee9e2e0af2f0292ec2d628012'
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    
    try:
        params = {
            'q': f"{location},UG",
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
    pest_alert = get_object_or_404(PestAlert, pk=pk)
    return render(request, 'weather/pest_alert_detail.html', {'pest_alert': pest_alert})