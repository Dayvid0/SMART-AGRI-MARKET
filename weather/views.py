import os
import json
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.cache import cache
from .models import WeatherAlert, PlantingSeason, PestAlert
from .services.farming_advisor import FarmingAdvisor
import requests
from datetime import datetime


def climate_suite(request):
    """
    Climate Suite dashboard. Renders the page skeleton IMMEDIATELY —
    weather data and recommendations are loaded client-side via AJAX
    so the user never stares at a blank screen.
    """
    active_alerts   = WeatherAlert.objects.filter(is_active=True, end_date__gte=timezone.now()).order_by('-severity')
    planting_seasons = PlantingSeason.objects.all()[:6]
    pest_alerts     = PestAlert.objects.filter(is_active=True)[:6]

    featured_districts = ['Kampala', 'Entebbe', 'Mbarara', 'Gulu', 'Jinja', 'Mbale']

    # Determine user's district for personalisation (no API call at this point)
    user_district = 'Kampala'
    if request.user.is_authenticated:
        user_district = (
            getattr(request.user, 'district', None)
            or getattr(request.user, 'location', None)
            or 'Kampala'
        )

    # Get zone info (pure Python — instant, no network call)
    advisor = FarmingAdvisor()
    region  = advisor.get_region_for_district(user_district)

    context = {
        'active_alerts':    active_alerts,
        'planting_seasons': planting_seasons,
        'pest_alerts':      pest_alerts,
        'featured_districts': featured_districts,
        'user_district':    user_district,
        'region':           region,
    }
    return render(request, 'weather/climate_suite.html', context)


@require_GET
def get_weather_api(request):
    """
    AJAX: Returns weather for a given district.
    Used by the district cards and the recommendation engine.
    Cached for 20 minutes per district.
    """
    district = request.GET.get('district', 'Kampala')
    cache_key = f'current_weather_{district.lower().replace(" ", "_")}'
    data = cache.get(cache_key)
    if data is None:
        data = _fetch_weather(district)
        if data:
            cache.set(cache_key, data, timeout=1200)  # 20 minutes

    if data:
        return JsonResponse(data)
    return JsonResponse({'error': 'Could not fetch weather data'}, status=400)


@require_GET
def get_recommendations_api(request):
    """
    AJAX: Returns full intelligent recommendations for a district.
    Called by the frontend after page paint — keeps initial page load instant.
    Cached for 30 minutes per district (advisor already caches forecast internally).
    """
    district = request.GET.get('district', 'Kampala')
    cache_key = f'full_recs_{district.lower().replace(" ", "_")}'
    result = cache.get(cache_key)

    if result is None:
        # Fetch weather first (may come from its own cache)
        weather = _fetch_weather(district)
        if not weather:
            return JsonResponse({'error': 'Weather unavailable'}, status=503)

        # Get active pest alerts from DB
        active_pest_alerts = list(PestAlert.objects.filter(is_active=True))

        # Get farmer's own crops from marketplace if authenticated
        farmer_crops = []
        if request.user.is_authenticated:
            try:
                from marketplace.models import Product
                farmer_crops = list(
                    Product.objects.filter(farmer=request.user, status='available')
                    .values_list('name', flat=True)
                )
            except Exception:
                pass

        advisor = FarmingAdvisor()
        result  = advisor.get_full_recommendations(
            district=district,
            weather=weather,
            active_pest_alerts=active_pest_alerts,
            farmer_crops=farmer_crops,
        )
        # Add weather into result for frontend convenience
        result['weather'] = weather
        cache.set(cache_key, result, timeout=1800)  # 30 minutes

    return JsonResponse(result, safe=False)


def _fetch_weather(location: str):
    """Internal helper — fetch current weather from OpenWeatherMap, with caching."""
    API_KEY  = os.environ.get('OPENWEATHER_API_KEY')
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    try:
        resp = requests.get(BASE_URL, params={
            'q': f"{location},UG",
            'appid': API_KEY,
            'units': 'metric'
        }, timeout=6)
        if resp.status_code == 200:
            d = resp.json()
            return {
                'temperature':  d['main']['temp'],
                'feels_like':   d['main']['feels_like'],
                'humidity':     d['main']['humidity'],
                'description':  d['weather'][0]['description'],
                'icon':         d['weather'][0]['icon'],
                'wind_speed':   d['wind']['speed'],
                'location':     location,
            }
    except Exception as e:
        print(f"[Weather] API error for {location}: {e}")
    return None


def pest_alert_detail(request, pk):
    pest_alert = get_object_or_404(PestAlert, pk=pk)
    return render(request, 'weather/pest_alert_detail.html', {'pest_alert': pest_alert})