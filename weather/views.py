from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from .models import WeatherAlert, PlantingSeason, PestAlert
from .services.farming_advisor import FarmingAdvisor
import requests
from datetime import datetime, date

def climate_suite(request):
    """
    Enhanced climate suite dashboard with weather, planting seasons, pest alerts,
    and intelligent farming recommendations
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
    user_location = request.user.location if request.user.is_authenticated and hasattr(request.user, 'location') and request.user.location else 'Kampala'
    weather_data = get_weather_data(user_location)
    
    # Initialize Farming Advisor
    advisor = FarmingAdvisor()
    
    # Generate intelligent recommendations
    planting_recommendations = []
    spray_recommendation = {}
    daily_activities = []
    
    if weather_data:
        planting_recommendations = advisor.get_planting_recommendations(user_location, weather_data)
        spray_recommendation = advisor.get_spray_recommendations(user_location, weather_data)
        daily_activities = advisor.get_daily_activities(weather_data)
    
    # Sample harvest predictions (in real app, get from user's planted crops)
    sample_planted_crops = [
        {'crop': 'maize', 'planted_date': date(2026, 1, 15)},
        {'crop': 'beans', 'planted_date': date(2026, 2, 1)},
    ]
    harvest_predictions = advisor.get_harvest_predictions(sample_planted_crops)
    
    context = {
        'active_alerts': active_alerts,
        'planting_seasons': planting_seasons,
        'pest_alerts': pest_alerts,
        'weather_data': weather_data,
        'featured_districts': featured_districts,
        # New intelligent recommendations
        'planting_recommendations': planting_recommendations,
        'spray_recommendation': spray_recommendation,
        'daily_activities': daily_activities,
        'harvest_predictions': harvest_predictions,
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