"""
Farming Advisor Service

Provides intelligent farming recommendations based on:
- Current weather conditions
- Weather forecasts
- Crop planting calendars
- Uganda agricultural best practices
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import requests


class FarmingAdvisor:
    """
    Generates actionable farming recommendations based on weather data
    """
    
    # Uganda crop planting seasons (simplified)
    CROP_SEASONS = {
        'maize': {
            'season_1': {'start': (3, 1), 'end': (5, 31)},  # March-May
            'season_2': {'start': (8, 1), 'end': (10, 31)},  # Aug-Oct
            'growth_days': 90,
            'optimal_temp': (20, 30),
            'min_rainfall_mm': 500
        },
        'beans': {
            'season_1': {'start': (3, 1), 'end': (5, 31)},
            'season_2': {'start': (9, 1), 'end': (11, 30)},
            'growth_days': 75,
            'optimal_temp': (18, 28),
            'min_rainfall_mm': 350
        },
        'cassava': {
            'season_1': {'start': (2, 1), 'end': (5, 31)},
            'season_2': {'start': (9, 1), 'end': (11, 30)},
            'growth_days': 270,
            'optimal_temp': (25, 35),
            'min_rainfall_mm': 1000
        },
        'tomatoes': {
            'season_1': {'start': (2, 1), 'end': (4, 30)},
            'season_2': {'start': (8, 1), 'end': (10, 31)},
            'growth_days': 80,
            'optimal_temp': (20, 28),
            'min_rainfall_mm': 400
        },
        'coffee': {
            'season_1': {'start': (3, 1), 'end': (5, 31)},
            'growth_days': 180,  # First harvest
            'optimal_temp': (18, 25),
            'min_rainfall_mm': 1200
        }
    }
    
    def __init__(self, api_key: str = 'be5fb80ee9e2e0af2f0292ec2d628012'):
        self.api_key = api_key
        self.base_url = 'http://api.openweathermap.org/data/2.5'
    
    def get_planting_recommendations(self, location: str, current_weather: Dict) -> List[Dict]:
        """
        Generate planting recommendations based on current season and weather
        
        Returns list of recommendations with crop, action, reason
        """
        recommendations = []
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        temp = current_weather.get('temperature', 25)
        humidity = current_weather.get('humidity', 70)
        
        # Get forecast to check for upcoming rain
        forecast = self._get_forecast(location)
        rain_next_3_days = self._check_rain_forecast(forecast, days=3)
        
        for crop, data in self.CROP_SEASONS.items():
            # Check if we're in planting season
            in_season = False
            for season_key in ['season_1', 'season_2']:
                if season_key in data:
                    season = data[season_key]
                    start_month, start_day = season['start']
                    end_month, end_day = season['end']
                    
                    if self._is_in_season(current_month, current_day, start_month, start_day, end_month, end_day):
                        in_season = True
                        break
            
            if in_season:
                optimal_temp_min, optimal_temp_max = data['optimal_temp']
                
                # Check conditions
                temp_ok = optimal_temp_min <= temp <= optimal_temp_max
                
                if temp_ok and not rain_next_3_days:
                    recommendations.append({
                        'crop': crop.capitalize(),
                        'action': 'plant',
                        'priority': 'high',
                        'reason': f'Optimal conditions: {temp}°C, no rain forecast for 3 days. Good soil preparation window.',
                        'icon': '🌱',
                        'color': 'success'
                    })
                elif temp_ok and rain_next_3_days:
                    recommendations.append({
                        'crop': crop.capitalize(),
                        'action': 'wait',
                        'priority': 'medium',
                        'reason': f'Temperature good ({temp}°C) but rain expected in 3 days. Wait for drier period.',
                        'icon': '⏳',
                        'color': 'warning'
                    })
                elif not temp_ok:
                    recommendations.append({
                        'crop': crop.capitalize(),
                        'action': 'monitor',
                        'priority': 'low',
                        'reason': f'Temperature {temp}°C outside optimal range ({optimal_temp_min}-{optimal_temp_max}°C).',
                        'icon': '📊',
                        'color': 'info'
                    })
        
        return recommendations[:5]  # Top 5 recommendations
    
    def get_harvest_predictions(self, planted_crops: List[Dict]) -> List[Dict]:
        """
        Predict harvest dates for planted crops
        
        Args:
            planted_crops: List of dicts with 'crop' and 'planted_date'
        
        Returns:
            List of harvest predictions
        """
        predictions = []
        
        for crop_data in planted_crops:
            crop_name = crop_data['crop'].lower()
            planted_date = crop_data['planted_date']
            
            if crop_name in self.CROP_SEASONS:
                growth_days = self.CROP_SEASONS[crop_name]['growth_days']
                harvest_date = planted_date + timedelta(days=growth_days)
                days_remaining = (harvest_date - date.today()).days
                
                predictions.append({
                    'crop': crop_name.capitalize(),
                    'planted_date': planted_date,
                    'harvest_date': harvest_date,
                    'days_remaining': days_remaining,
                    'progress_percent': int(((growth_days - days_remaining) / growth_days) * 100) if days_remaining > 0 else 100
                })
        
        return predictions
    
    def get_spray_recommendations(self, location: str, current_weather: Dict) -> Dict:
        """
        Recommend optimal spray timing based on weather
        
        Returns recommendation with timing and reasoning
        """
        forecast = self._get_forecast(location)
        
        # Check conditions for next 24 hours
        rain_24h = self._check_rain_forecast(forecast, days=1)
        wind_speed = current_weather.get('wind_speed', 0)
        temp = current_weather.get('temperature', 25)
        
        # Ideal spray conditions
        if not rain_24h and wind_speed < 15 and 18 <= temp <= 30:
            return {
                'recommendation': 'spray_now',
                'title': '✅ Excellent Spray Conditions',
                'message': f'No rain for 24hrs, low wind ({wind_speed}km/h), optimal temp ({temp}°C). Apply pesticides/herbicides now.',
                'color': 'success',
                'urgency': 'high'
            }
        elif rain_24h:
            hours_to_rain = self._hours_until_rain(forecast)
            return {
                'recommendation': 'delay',
                'title': '⚠️ Delay Spraying',
                'message': f'Rain expected in {hours_to_rain} hours. Wait for clearer weather to avoid wash-off.',
                'color': 'warning',
                'urgency': 'medium'
            }
        elif wind_speed >= 15:
            return {
                'recommendation': 'wait_wind',
                'title': '🌬️ High Wind Alert',
                'message': f'Wind speed {wind_speed}km/h too high. Risk of spray drift. Wait for calmer conditions.',
                'color': 'danger',
                'urgency': 'high'
            }
        else:
            return {
                'recommendation': 'monitor',
                'title': '📊 Monitor Conditions',
                'message': 'Conditions acceptable but not ideal. Check forecast again before spraying.',
                'color': 'info',
                'urgency': 'low'
            }
    
    def get_daily_activities(self, current_weather: Dict, forecast: List = None) -> List[Dict]:
        """
        Suggest farming activities for today based on weather
        """
        activities = []
        temp = current_weather.get('temperature', 25)
        humidity = current_weather.get('humidity', 70)
        description = current_weather.get('description', '').lower()
        
        # Check if raining
        is_raining = 'rain' in description
        
        if not is_raining and temp < 30:
            activities.append({
                'activity': 'Land Preparation',
                'icon': '🚜',
                'reason': 'Dry conditions, moderate temperature. Good for plowing/tilling.',
                'priority': 'high'
            })
        
        if not is_raining and humidity < 60:
            activities.append({
                'activity': 'Harvesting',
                'icon': '🌾',
                'reason': 'Low humidity reduces crop moisture. Ideal for harvesting and drying.',
                'priority': 'high'
            })
        
        if is_raining or humidity > 80:
            activities.append({
                'activity': 'Skip Irrigation',
                'icon': '💧',
                'reason': 'High humidity/rain. No need for irrigation today.',
                'priority': 'medium'
            })
        
        if temp > 28 and not is_raining:
            activities.append({
                'activity': 'Weed Control',
                'icon': '🌿',
                'reason': 'Warm, dry weather. Good for manual weeding (weeds easier to uproot).',
                'priority': 'medium'
            })
        
        if 'clear' in description or 'sun' in description:
            activities.append({
                'activity': 'Crop Drying',
                'icon': '☀️',
                'reason': 'Sunny weather perfect for drying harvested crops.',
                'priority': 'high'
            })
        
        return activities[:4]  # Top 4 activities
    
    def _get_forecast(self, location: str, days: int = 5) -> List[Dict]:
        """Fetch weather forecast from API"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': f"{location},UG",
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json().get('list', [])
        except:
            pass
        return []
    
    def _check_rain_forecast(self, forecast: List[Dict], days: int = 3) -> bool:
        """Check if rain is forecast in next N days"""
        if not forecast:
            return False
        
        cutoff = datetime.now() + timedelta(days=days)
        for item in forecast:
            forecast_time = datetime.fromtimestamp(item['dt'])
            if forecast_time > cutoff:
                break
            
            weather = item.get('weather', [{}])[0]
            if 'rain' in weather.get('main', '').lower():
                return True
        
        return False
    
    def _hours_until_rain(self, forecast: List[Dict]) -> int:
        """Calculate hours until next rain"""
        if not forecast:
            return 24
        
        for item in forecast:
            weather = item.get('weather', [{}])[0]
            if 'rain' in weather.get('main', '').lower():
                forecast_time = datetime.fromtimestamp(item['dt'])
                hours = (forecast_time - datetime.now()).total_seconds() / 3600
                return int(hours)
        
        return 24
    
    def _is_in_season(self, current_month, current_day, start_month, start_day, end_month, end_day) -> bool:
        """Check if current date is within season"""
        current = (current_month, current_day)
        start = (start_month, start_day)
        end = (end_month, end_day)
        
        if start <= end:
            return start <= current <= end
        else:  # Season crosses year boundary
            return current >= start or current <= end
