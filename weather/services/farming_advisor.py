"""
farming_advisor.py — Uganda Smart Agri Advisor (v2)

Provides region-aware, crop-specific, weather-triggered intelligence including:
  - Uganda Agroecological Zone mapping (5 zones, 80+ districts)
  - Region-specific crop calendars with week-by-week activity guidance
  - Weather-triggered disease risk scoring per crop
  - Active pest/disease alert integration
  - Farmer crop cross-referencing from their marketplace listings
  - Cached API calls to prevent repeated network hits
"""

import os
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import requests
from django.core.cache import cache


# ============================================================
#  UGANDA AGROECOLOGICAL ZONES
#  Based on NARO / FAO Uganda crop zone data
# ============================================================

UGANDA_ZONES = {
    'lake_victoria_crescent': {
        'name': 'Lake Victoria Crescent',
        'icon': '🌊',
        'description': 'High rainfall bimodal zone around Lake Victoria. Rich volcanic soils.',
        'districts': [
            'Kampala', 'Wakiso', 'Mukono', 'Jinja', 'Iganga', 'Bugiri', 'Mayuge',
            'Masaka', 'Kalungu', 'Lwengo', 'Bukomansimbi', 'Rakai', 'Kyotera',
        ],
        'rainfall_mm': '1200–1800',
        'seasons': {
            'season_1': {'name': 'Long Rains', 'start': (3, 1),  'end': (5, 31)},
            'season_2': {'name': 'Short Rains', 'start': (10, 1), 'end': (12, 15)},
        },
        'primary_crops': ['matooke', 'coffee_arabica', 'vanilla', 'sugarcane', 'beans', 'maize', 'tomatoes'],
        'crops': {
            'matooke': {
                'local_name': 'Matooke (Cooking Banana)',
                'growth_days': 365,
                'plant_months': [3, 4, 10, 11],
                'optimal_temp': (20, 30),
                'optimal_humidity': (65, 90),
                'rainfall_mm': 1200,
                'pests': ['banana_weevil', 'black_sigatoka', 'banana_xanthomonas_wilt'],
                'soil': 'Deep, well-drained loamy soils',
            },
            'coffee_arabica': {
                'local_name': 'Arabica Coffee',
                'growth_days': 270,
                'plant_months': [3, 4, 5, 10, 11],
                'optimal_temp': (18, 24),
                'optimal_humidity': (60, 80),
                'rainfall_mm': 1500,
                'pests': ['coffee_berry_borer', 'coffee_leaf_rust', 'antestia_bug'],
                'soil': 'Rich, humus-rich volcanic soils',
            },
            'beans': {
                'local_name': 'Common Beans',
                'growth_days': 75,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (18, 27),
                'optimal_humidity': (50, 75),
                'rainfall_mm': 400,
                'pests': ['bean_fly', 'bean_pod_borer', 'angular_leaf_spot'],
                'soil': 'Loamy, well-drained',
            },
            'maize': {
                'local_name': 'Maize (Corn)',
                'growth_days': 90,
                'plant_months': [3, 4, 8, 9],
                'optimal_temp': (20, 30),
                'optimal_humidity': (50, 80),
                'rainfall_mm': 500,
                'pests': ['fall_armyworm', 'stem_borer', 'maize_streak_virus'],
                'soil': 'Well-drained sandy-loam',
            },
            'tomatoes': {
                'local_name': 'Tomatoes',
                'growth_days': 80,
                'plant_months': [2, 3, 8, 9],
                'optimal_temp': (20, 28),
                'optimal_humidity': (50, 70),
                'rainfall_mm': 400,
                'pests': ['late_blight', 'tuta_absoluta', 'bacterial_wilt'],
                'soil': 'Sandy loam, well-drained, pH 6.0–6.8',
            },
        },
    },

    'eastern_highlands': {
        'name': 'Eastern Highlands',
        'icon': '⛰️',
        'description': 'Mt Elgon slopes. Cool, high-altitude zone with fertile volcanic soils.',
        'districts': [
            'Mbale', 'Sironko', 'Bududa', 'Manafwa', 'Bulambuli', 'Kapchorwa',
            'Kween', 'Bukwo', 'Tororo', 'Busia',
        ],
        'rainfall_mm': '1400–2000',
        'seasons': {
            'season_1': {'name': 'Long Rains', 'start': (3, 1),  'end': (6, 30)},
            'season_2': {'name': 'Short Rains', 'start': (9, 1), 'end': (12, 15)},
        },
        'primary_crops': ['irish_potato', 'arabica_coffee', 'wheat', 'sorghum', 'beans', 'maize'],
        'crops': {
            'irish_potato': {
                'local_name': 'Irish Potato (Victoria / Kachpot)',
                'growth_days': 90,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (12, 22),
                'optimal_humidity': (60, 85),
                'rainfall_mm': 500,
                'pests': ['late_blight', 'potato_tuber_moth', 'aphids'],
                'soil': 'Well-drained, slightly acidic volcanic loam',
                'disease_risk_rules': [
                    {
                        'disease': 'Late Blight (Phytophthora infestans)',
                        'trigger': 'humidity > 80 and 10 <= temp <= 20',
                        'severity': 'critical',
                        'action': 'Apply Mancozeb (Dithane M-45) or Ridomil Gold immediately. Avoid overhead irrigation.',
                        'icon': '🦠',
                    }
                ],
            },
            'arabica_coffee': {
                'local_name': 'Arabica Coffee (Mt Elgon)',
                'growth_days': 270,
                'plant_months': [3, 4, 5, 9, 10],
                'optimal_temp': (15, 24),
                'optimal_humidity': (60, 80),
                'rainfall_mm': 1400,
                'pests': ['coffee_leaf_rust', 'coffee_berry_borer', 'antestia_bug'],
                'soil': 'Deep volcanic loam, pH 5.5–6.5',
            },
            'wheat': {
                'local_name': 'Wheat',
                'growth_days': 120,
                'plant_months': [3, 4, 9],
                'optimal_temp': (12, 22),
                'optimal_humidity': (50, 70),
                'rainfall_mm': 450,
                'pests': ['wheat_rust', 'aphids', 'hessian_fly'],
                'soil': 'Well-drained loam, pH 6.0–7.0',
            },
            'beans': {
                'local_name': 'Common Beans',
                'growth_days': 75,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (15, 25),
                'optimal_humidity': (50, 75),
                'rainfall_mm': 350,
                'pests': ['bean_fly', 'angular_leaf_spot', 'bean_rust'],
                'soil': 'Loamy, well-drained',
            },
            'maize': {
                'local_name': 'Maize (High-Altitude Varieties)',
                'growth_days': 100,
                'plant_months': [3, 4, 8, 9],
                'optimal_temp': (16, 28),
                'optimal_humidity': (50, 80),
                'rainfall_mm': 500,
                'pests': ['fall_armyworm', 'turcicum_leaf_blight', 'grey_leaf_spot'],
                'soil': 'Well-drained loam',
            },
        },
    },

    'northern_savanna': {
        'name': 'Northern Savanna',
        'icon': '🌾',
        'description': 'Semi-arid savanna with unimodal rainfall. Historically conflict-affected; now recovering strongly.',
        'districts': [
            'Gulu', 'Omoro', 'Nwoya', 'Amuru', 'Kitgum', 'Pader', 'Agago',
            'Lira', 'Alebtong', 'Oyam', 'Kole', 'Apac', 'Dokolo',
            'Soroti', 'Serere', 'Ngora', 'Kumi', 'Bukedea',
        ],
        'rainfall_mm': '900–1300',
        'seasons': {
            'season_1': {'name': 'Main Rains (Unimodal)', 'start': (4, 1), 'end': (10, 31)},
        },
        'primary_crops': ['maize', 'sorghum', 'simsim', 'groundnuts', 'cassava', 'sunflower'],
        'crops': {
            'maize': {
                'local_name': 'Maize (Longe 10H, NARO 603)',
                'growth_days': 90,
                'plant_months': [4, 5, 6],
                'optimal_temp': (22, 32),
                'optimal_humidity': (40, 75),
                'rainfall_mm': 600,
                'pests': ['fall_armyworm', 'stem_borer', 'northern_leaf_blight'],
                'soil': 'Sandy-loam savanna soils',
                'disease_risk_rules': [
                    {
                        'disease': 'Fall Armyworm (Spodoptera frugiperda)',
                        'trigger': 'humidity > 65 and temp > 24',
                        'severity': 'high',
                        'action': 'Scout fields at dawn/dusk. Apply Emamectin Benzoate or Chlorpyrifos at whorl stage. Use pheromone traps.',
                        'icon': '🐛',
                    }
                ],
            },
            'sorghum': {
                'local_name': 'Sorghum (Seso 3, Seredo)',
                'growth_days': 120,
                'plant_months': [4, 5, 6],
                'optimal_temp': (25, 35),
                'optimal_humidity': (35, 65),
                'rainfall_mm': 400,
                'pests': ['sorghum_midge', 'head_bugs', 'leaf_anthracnose'],
                'soil': 'Well-drained, tolerates poor soils',
            },
            'groundnuts': {
                'local_name': 'Groundnuts (Serenut 4T)',
                'growth_days': 110,
                'plant_months': [4, 5, 6],
                'optimal_temp': (24, 33),
                'optimal_humidity': (40, 70),
                'rainfall_mm': 500,
                'pests': ['groundnut_rosette', 'leaf_spot', 'aflatoxin_fungi'],
                'soil': 'Sandy loam, well-drained, pH 5.5–7.0',
            },
            'simsim': {
                'local_name': 'Sim Sim (Sesame)',
                'growth_days': 90,
                'plant_months': [4, 5, 7],
                'optimal_temp': (26, 35),
                'optimal_humidity': (30, 65),
                'rainfall_mm': 300,
                'pests': ['phytophthora_blight', 'cercospora_leaf_spot'],
                'soil': 'Light-textured, well-drained',
            },
            'cassava': {
                'local_name': 'Cassava (NASE 14, NASE 19)',
                'growth_days': 270,
                'plant_months': [3, 4, 5, 9, 10],
                'optimal_temp': (25, 35),
                'optimal_humidity': (50, 80),
                'rainfall_mm': 600,
                'pests': ['cassava_brown_streak', 'cassava_mosaic', 'whitefly'],
                'soil': 'Loamy-sandy, tolerates acidic soils',
            },
        },
    },

    'western_highlands': {
        'name': 'Western Highlands (Kigezi)',
        'icon': '🏔️',
        'description': 'High-altitude, cool Kigezi plateau. Heavy rainfall. Famous for potatoes and pyrethrum.',
        'districts': [
            'Mbarara', 'Isingiro', 'Kiruhura', 'Ibanda', 'Bushenyi',
            'Mitooma', 'Rubirizi', 'Sheema', 'Buhweju',
            'Kabale', 'Rukiga', 'Rubanda',
            'Kisoro', 'Kanungu', 'Rukungiri',
        ],
        'rainfall_mm': '1000–1800',
        'seasons': {
            'season_1': {'name': 'Long Rains', 'start': (3, 1), 'end': (5, 31)},
            'season_2': {'name': 'Short Rains', 'start': (9, 1), 'end': (12, 31)},
        },
        'primary_crops': ['irish_potato', 'matooke', 'pyrethrum', 'beans', 'maize', 'dairy_pasture'],
        'crops': {
            'irish_potato': {
                'local_name': 'Irish Potato (Kabale / Kigezi)',
                'growth_days': 90,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (10, 20),
                'optimal_humidity': (65, 90),
                'rainfall_mm': 500,
                'pests': ['late_blight', 'potato_cyst_nematode', 'aphids', 'bacterial_wilt'],
                'soil': 'Well-drained, slightly acidic, terraced fields',
                'disease_risk_rules': [
                    {
                        'disease': 'Late Blight (Phytophthora infestans)',
                        'trigger': 'humidity > 80 and temp < 20',
                        'severity': 'critical',
                        'action': 'Apply Mancozeb preventively every 7–10 days. Destroy infected plants. Avoid waterlogging.',
                        'icon': '🦠',
                    }
                ],
            },
            'matooke': {
                'local_name': 'Matooke (Nshonge variety)',
                'growth_days': 365,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (20, 30),
                'optimal_humidity': (65, 90),
                'rainfall_mm': 1200,
                'pests': ['banana_weevil', 'black_sigatoka', 'nematodes'],
                'soil': 'Deep well-drained loam, pH 5.5–7.0',
            },
            'pyrethrum': {
                'local_name': 'Pyrethrum (Cash Crop)',
                'growth_days': 180,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (10, 20),
                'optimal_humidity': (60, 80),
                'rainfall_mm': 800,
                'pests': ['aphids', 'thrips', 'powdery_mildew'],
                'soil': 'Well-drained, fertile, slightly acidic',
            },
            'beans': {
                'local_name': 'Common Beans / Climbing Beans',
                'growth_days': 80,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (15, 25),
                'optimal_humidity': (55, 80),
                'rainfall_mm': 350,
                'pests': ['angular_leaf_spot', 'bean_rust', 'anthracnose'],
                'soil': 'Well-drained fertile loam',
            },
        },
    },

    'nile_basin_west_nile': {
        'name': 'Nile Basin / West Nile',
        'icon': '🌿',
        'description': 'Flat-to-hilly zone around Albert Nile and Lake Albert. Fertile, tropical.',
        'districts': [
            'Hoima', 'Buliisa', 'Masindi', 'Kiryandongo',
            'Arua', 'Zombo', 'Nebbi', 'Pakwach', 'Madi-Okollo',
            'Koboko', 'Yumbe', 'Moyo', 'Adjumani',
        ],
        'rainfall_mm': '1000–1500',
        'seasons': {
            'season_1': {'name': 'Long Rains', 'start': (3, 1), 'end': (5, 31)},
            'season_2': {'name': 'Short Rains', 'start': (9, 1), 'end': (11, 30)},
        },
        'primary_crops': ['cassava', 'cotton', 'sunflower', 'tobacco', 'maize', 'sweet_potato'],
        'crops': {
            'cassava': {
                'local_name': 'Cassava (NASE 14, TME 204)',
                'growth_days': 270,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (25, 35),
                'optimal_humidity': (50, 80),
                'rainfall_mm': 600,
                'pests': ['cassava_brown_streak', 'cassava_mosaic', 'whitefly', 'green_mite'],
                'soil': 'Sandy loam, well-drained',
                'disease_risk_rules': [
                    {
                        'disease': 'Cassava Brown Streak Disease (CBSD)',
                        'trigger': 'humidity > 75',
                        'severity': 'high',
                        'action': 'Rogue out infected plants. Use certified CBSD-tolerant varieties. Control whitefly vectors with neem extract.',
                        'icon': '🍂',
                    }
                ],
            },
            'cotton': {
                'local_name': 'Cotton (Albar)',
                'growth_days': 150,
                'plant_months': [4, 5, 6],
                'optimal_temp': (28, 37),
                'optimal_humidity': (40, 70),
                'rainfall_mm': 700,
                'pests': ['bollworm', 'cotton_stainer', 'aphids', 'jassids'],
                'soil': 'Heavy clay loam, pH 5.8–8.0',
            },
            'sunflower': {
                'local_name': 'Sunflower (Sunfola)',
                'growth_days': 100,
                'plant_months': [4, 5, 9],
                'optimal_temp': (25, 35),
                'optimal_humidity': (40, 70),
                'rainfall_mm': 450,
                'pests': ['sunflower_aphids', 'alternaria_blight'],
                'soil': 'Sandy loam, well-drained',
            },
            'sweet_potato': {
                'local_name': 'Sweet Potato (SPK 004 / Kakamega)',
                'growth_days': 120,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (22, 32),
                'optimal_humidity': (50, 80),
                'rainfall_mm': 500,
                'pests': ['sweet_potato_weevil', 'sweet_potato_virus', 'leaf_folder'],
                'soil': 'Sandy loam, well-drained, pH 5.5–6.5',
            },
            'maize': {
                'local_name': 'Maize (Longe 5)',
                'growth_days': 90,
                'plant_months': [3, 4, 9, 10],
                'optimal_temp': (22, 32),
                'optimal_humidity': (45, 78),
                'rainfall_mm': 500,
                'pests': ['fall_armyworm', 'stem_borer', 'striga_weed'],
                'soil': 'Well-drained sandy-loam',
            },
        },
    },
}

# ============================================================
#  PEST KNOWLEDGE BASE — weather-triggered risk thresholds
# ============================================================

PEST_KNOWLEDGE = {
    'fall_armyworm': {
        'name': 'Fall Armyworm',
        'scientific': 'Spodoptera frugiperda',
        'icon': '🐛',
        'risk_when': 'Warm nights (>20°C) + humid conditions (>65%) accelerate egg-hatching.',
        'control': 'Apply Emamectin Benzoate (Coragen) or Chlorpyrifos at whorl stage. Scout at dawn.',
        'prevention': 'Use pheromone traps for early detection. Intercrop with legumes.',
    },
    'late_blight': {
        'name': 'Late Blight',
        'scientific': 'Phytophthora infestans',
        'icon': '🦠',
        'risk_when': 'Cool temperatures (10–20°C) + high humidity (>80%) for 2+ days.',
        'control': 'Apply Mancozeb (Dithane M-45) or Ridomil Gold every 7 days. Remove infected haulm.',
        'prevention': 'Plant certified seed. Avoid overhead irrigation. Ensure good airflow between plants.',
    },
    'coffee_berry_borer': {
        'name': 'Coffee Berry Borer',
        'scientific': 'Hypothenemus hampei',
        'icon': '🪲',
        'risk_when': 'Temperatures 20–30°C with sustained humidity after fruit set.',
        'control': 'Regular harvesting of all ripe and overripe berries. Apply Beauveria bassiana (biological).',
        'prevention': 'Maintain shade trees. Strip-harvest every 2–3 weeks.',
    },
    'black_sigatoka': {
        'name': 'Black Sigatoka',
        'scientific': 'Mycosphaerella fijiensis',
        'icon': '🍌',
        'risk_when': 'Prolonged leaf wetness + temperatures 25–28°C.',
        'control': 'Apply Propiconazole or Mancozeb every 3 weeks. Remove and destroy infected leaves.',
        'prevention': 'Adequate spacing (3×3m). Remove dead leaves regularly.',
    },
    'cassava_brown_streak': {
        'name': 'Cassava Brown Streak Disease',
        'scientific': 'CBSD (UCBSV/CBSV)',
        'icon': '🍂',
        'risk_when': 'High whitefly populations during humid periods.',
        'control': 'Rogue infected plants immediately. Plant CBSD-tolerant varieties (NASE 14, NASE 19).',
        'prevention': 'Use clean planting material. Control whitefly with neem. Inspect nurseries.',
    },
    'banana_xanthomonas_wilt': {
        'name': 'Banana Xanthomonas Wilt (BXW)',
        'scientific': 'Xanthomonas vasicola pv. musacearum',
        'icon': '⚠️',
        'risk_when': 'Spread by insects, contaminated tools, and infected planting material.',
        'control': 'Rogue infected mats. Destroy by burning. Sterilise tools with bleach between plants.',
        'prevention': 'Use certified clean suckers. De-bud male flowers using a clean forked stick.',
    },
}

# ============================================================
#  WEEKLY FARMING CALENDAR — what to do each week of the season
# ============================================================

WEEKLY_CALENDAR = {
    1:  {'label': 'Week 1–2', 'activity': 'Land Preparation', 'icon': '🚜', 'detail': 'Deep plough or till. Remove crop residues from last season. Soil test if possible.'},
    2:  {'label': 'Week 2–3', 'activity': 'Soil Amendment',   'icon': '🌱', 'detail': 'Apply lime if soil is acidic (pH < 5.5). Incorporate organic manure or compost.'},
    3:  {'label': 'Week 3–4', 'activity': 'Planting',         'icon': '🌾', 'detail': 'Plant at recommended spacing. Apply basal fertiliser (DAP) in seed furrows.'},
    5:  {'label': 'Week 5–6', 'activity': 'First Weeding',    'icon': '🪴', 'detail': 'Remove weeds before they compete. Apply pre-emergent herbicide if needed.'},
    7:  {'label': 'Week 7',   'activity': 'Top-Dressing',     'icon': '💊', 'detail': 'Apply CAN or Urea fertiliser beside plant stem (not directly on stem).'},
    8:  {'label': 'Week 8',   'activity': 'Pest Scouting',    'icon': '🔍', 'detail': 'Scout every 3 days. Check undersides of leaves. Record pest counts.'},
    10: {'label': 'Week 10',  'activity': 'Second Weeding',   'icon': '🌿', 'detail': 'Final weed before canopy closes. Side-dress with additional nitrogen if needed.'},
    12: {'label': 'Week 12',  'activity': 'Pre-Harvest Assessment', 'icon': '📋', 'detail': 'Test grain/fruit maturity. Arrange transport and storage logistics.'},
    14: {'label': 'Week 14+', 'activity': 'Harvest',          'icon': '🌾', 'detail': 'Harvest at correct moisture content. Dry thoroughly before storage.'},
}


class FarmingAdvisor:
    """
    Region-aware, weather-driven farming intelligence engine for Uganda.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY', '')
        self.base_url = 'http://api.openweathermap.org/data/2.5'

    # ----------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------

    def get_region_for_district(self, district: str) -> Optional[Dict]:
        """Return the agroecological zone dict for a given district name."""
        district_clean = district.strip().title()
        for zone_key, zone in UGANDA_ZONES.items():
            if district_clean in zone['districts']:
                return {'key': zone_key, **zone}
        # Default to Lake Victoria Crescent if unknown
        z = UGANDA_ZONES['lake_victoria_crescent']
        return {'key': 'lake_victoria_crescent', **z}

    def get_full_recommendations(self, district: str, weather: Dict, active_pest_alerts=None, farmer_crops: List[str] = None) -> Dict:
        """
        Master method — returns everything the dashboard needs in one call.
        Cached per district+hour to avoid redundant API hits.
        """
        region = self.get_region_for_district(district)
        forecast = self._get_forecast_cached(district)
        rain_24h = self._check_rain_forecast(forecast, days=1)
        rain_3d  = self._check_rain_forecast(forecast, days=3)

        result = {
            'region': {
                'name': region['name'],
                'icon': region['icon'],
                'description': region['description'],
                'districts': region['districts'][:6],
                'rainfall_mm': region['rainfall_mm'],
                'primary_crops': region.get('primary_crops', []),
            },
            'current_season': self._get_current_season(region),
            'weekly_calendar': self._get_calendar_for_today(region),
            'crop_recommendations': self._get_crop_recommendations(region, weather, rain_3d, farmer_crops),
            'disease_risk': self._get_disease_risk(region, weather),
            'spray_recommendation': self._get_spray_rec(weather, rain_24h, forecast),
            'daily_activities': self._get_daily_activities(weather),
            'pest_alerts_for_region': self._match_pest_alerts(region, active_pest_alerts or []),
            'rain_forecast': {
                'rain_24h': rain_24h,
                'rain_3d': rain_3d,
                'hours_until_rain': self._hours_until_rain(forecast),
            },
        }
        return result

    # ----------------------------------------------------------
    # REGION & SEASON
    # ----------------------------------------------------------

    def _get_current_season(self, region: Dict) -> Optional[Dict]:
        """Identify which growing season we are currently in for this zone."""
        now = datetime.now()
        for season_key, season in region.get('seasons', {}).items():
            start_m, start_d = season['start']
            end_m, end_d     = season['end']
            start = datetime(now.year, start_m, start_d)
            end   = datetime(now.year, end_m, end_d)
            if start <= now <= end:
                days_in    = (now - start).days
                total_days = (end - start).days
                return {
                    'name': season['name'],
                    'start': start.strftime('%b %d'),
                    'end': end.strftime('%b %d'),
                    'days_in': days_in,
                    'total_days': total_days,
                    'progress_pct': min(int(days_in / total_days * 100), 100),
                    'week_number': days_in // 7 + 1,
                }
        # Between seasons
        return {
            'name': 'Between Seasons (Land Prep)',
            'start': '—', 'end': '—',
            'days_in': 0, 'total_days': 1, 'progress_pct': 0, 'week_number': 0,
        }

    def _get_calendar_for_today(self, region: Dict) -> List[Dict]:
        """Return the current + upcoming weekly calendar tasks."""
        season = self._get_current_season(region)
        week = season.get('week_number', 0)
        tasks = []
        sorted_weeks = sorted(WEEKLY_CALENDAR.keys())
        current_found = False
        for w in sorted_weeks:
            task = dict(WEEKLY_CALENDAR[w])
            if w <= week:
                task['status'] = 'done' if w < week else 'current'
            else:
                task['status'] = 'upcoming'
            if task['status'] == 'current':
                current_found = True
            tasks.append(task)
        return tasks[:6]  # Show 6 tasks

    # ----------------------------------------------------------
    # CROP RECOMMENDATIONS (region + weather aware)
    # ----------------------------------------------------------

    def _get_crop_recommendations(self, region: Dict, weather: Dict, rain_3d: bool, farmer_crops: List[str] = None) -> List[Dict]:
        """Generate crop-specific planting/action recommendations for this region."""
        recs = []
        temp     = weather.get('temperature', 25)
        humidity = weather.get('humidity', 70)
        now_month = datetime.now().month

        # Prioritise farmer's own crops if known
        zone_crops = region.get('crops', {})
        crop_keys  = list(zone_crops.keys())

        if farmer_crops:
            # Put farmer's crops first
            known = [c.lower().replace(' ', '_') for c in farmer_crops]
            crop_keys = [k for k in crop_keys if k in known] + [k for k in crop_keys if k not in known]

        for crop_key in crop_keys:
            crop = zone_crops[crop_key]
            in_planting_window = now_month in crop.get('plant_months', [])
            opt_min, opt_max   = crop.get('optimal_temp', (20, 30))
            temp_ok            = opt_min <= temp <= opt_max
            humidity_ok        = crop.get('optimal_humidity', (50, 80))[0] <= humidity <= crop.get('optimal_humidity', (50, 80))[1]

            if in_planting_window:
                if temp_ok and not rain_3d:
                    recs.append({
                        'crop':    crop['local_name'],
                        'region':  region['name'],
                        'action':  '🌱 Plant Now',
                        'priority': 'high',
                        'color':   'success',
                        'detail':  (
                            f"Optimal conditions for {crop['local_name']} in the {region['name']} zone. "
                            f"Temperature {temp:.0f}°C (ideal: {opt_min}–{opt_max}°C). No rain expected for 3 days — ideal soil prep window. "
                            f"Soil type: {crop.get('soil', 'well-drained loam')}."
                        ),
                        'pests_to_watch': [PEST_KNOWLEDGE.get(p, {}).get('name', p.replace('_', ' ').title()) for p in crop.get('pests', [])[:2]],
                    })
                elif temp_ok and rain_3d:
                    recs.append({
                        'crop':    crop['local_name'],
                        'region':  region['name'],
                        'action':  '⏳ Wait — Rain Coming',
                        'priority': 'medium',
                        'color':   'warning',
                        'detail':  (
                            f"Temperature ideal ({temp:.0f}°C) for {crop['local_name']} but rain is forecast in the next 3 days. "
                            f"Delay planting to avoid waterlogging and damping-off. Use this time to prepare seedbeds."
                        ),
                        'pests_to_watch': [PEST_KNOWLEDGE.get(p, {}).get('name', p.replace('_', ' ').title()) for p in crop.get('pests', [])[:2]],
                    })
                elif not temp_ok:
                    recs.append({
                        'crop':    crop['local_name'],
                        'region':  region['name'],
                        'action':  '📊 Monitor — Temperature Off',
                        'priority': 'low',
                        'color':   'info',
                        'detail':  (
                            f"Current temperature {temp:.0f}°C is outside the optimal range ({opt_min}–{opt_max}°C) for {crop['local_name']}. "
                            f"Monitor weather and prepare materials. Plant when temps stabilise."
                        ),
                        'pests_to_watch': [],
                    })
            else:
                # Not planting season — give maintenance advice
                recs.append({
                    'crop':    crop['local_name'],
                    'region':  region['name'],
                    'action':  '🔍 Scout & Maintain',
                    'priority': 'low',
                    'color':   'secondary',
                    'detail':  (
                        f"Not in the primary planting window for {crop['local_name']} in {region['name']}. "
                        f"Scout established fields for pest pressure. Prepare inputs for the next season."
                    ),
                    'pests_to_watch': [PEST_KNOWLEDGE.get(p, {}).get('name', p.replace('_', ' ').title()) for p in crop.get('pests', [])[:2]],
                })

        return recs[:5]

    # ----------------------------------------------------------
    # DISEASE RISK ENGINE
    # ----------------------------------------------------------

    def _get_disease_risk(self, region: Dict, weather: Dict) -> List[Dict]:
        """Check weather-triggered disease risk thresholds for each crop in this region."""
        risks = []
        temp     = weather.get('temperature', 25)
        humidity = weather.get('humidity', 70)

        for crop_key, crop in region.get('crops', {}).items():
            for rule in crop.get('disease_risk_rules', []):
                trigger_expr = rule['trigger']
                try:
                    # Safe eval of simple condition strings like "humidity > 80 and temp < 20"
                    triggered = eval(trigger_expr, {'humidity': humidity, 'temp': temp})
                except Exception:
                    triggered = False

                if triggered:
                    risks.append({
                        'crop': crop['local_name'],
                        'disease': rule['disease'],
                        'severity': rule['severity'],
                        'action': rule['action'],
                        'icon': rule.get('icon', '⚠️'),
                        'color': 'danger' if rule['severity'] == 'critical' else 'warning',
                        'trigger_detail': f"Current: humidity {humidity:.0f}%, temp {temp:.0f}°C",
                    })

        # Also check PEST_KNOWLEDGE global rules based on weather
        if humidity > 80 and temp > 22:
            risks.append({
                'crop': 'All crops',
                'disease': 'General Fungal Pressure',
                'severity': 'medium',
                'action': 'Ensure adequate spacing and airflow. Avoid overhead irrigation. Apply preventive fungicides on susceptible crops.',
                'icon': '🍄',
                'color': 'warning',
                'trigger_detail': f"High humidity ({humidity:.0f}%) + warm temp ({temp:.0f}°C) = elevated fungal risk.",
            })

        return risks

    # ----------------------------------------------------------
    # PEST ALERT MATCHING
    # ----------------------------------------------------------

    def _match_pest_alerts(self, region: Dict, active_pest_alerts) -> List[Dict]:
        """Filter database PestAlerts to only those relevant to this region's districts."""
        matched = []
        region_districts = [d.lower() for d in region.get('districts', [])]
        for alert in active_pest_alerts:
            alert_regions = [r.strip().lower() for r in alert.affected_regions.split(',')]
            if any(ar in region_districts or ar in region['name'].lower() for ar in alert_regions):
                matched.append({
                    'name': alert.pest_name,
                    'severity': alert.severity,
                    'affected_crops': alert.affected_crops,
                    'description': alert.description,
                    'control_measures': alert.control_measures,
                    'color': 'danger' if alert.severity == 'high' else 'warning',
                })
        return matched

    # ----------------------------------------------------------
    # SPRAY & ACTIVITY RECOMMENDATIONS
    # ----------------------------------------------------------

    def _get_spray_rec(self, weather: Dict, rain_24h: bool, forecast) -> Dict:
        wind_speed = weather.get('wind_speed', 0)
        temp       = weather.get('temperature', 25)
        humidity   = weather.get('humidity', 70)
        if not rain_24h and wind_speed < 15 and 18 <= temp <= 32:
            quality = 'Excellent' if (wind_speed < 8 and humidity < 75) else 'Good'
            return {
                'status': 'spray_now',
                'title':  f'✅ {quality} Spray Conditions',
                'message': (
                    f"Wind {wind_speed:.0f} km/h, temp {temp:.0f}°C, humidity {humidity:.0f}%. "
                    f"Spray early morning (06:00–09:00) or evening (16:00–18:00) for best coverage and minimal drift."
                ),
                'color': 'success',
            }
        elif rain_24h:
            hrs = self._hours_until_rain(forecast)
            return {
                'status': 'delay',
                'title':  '🌧️ Delay Spraying',
                'message': (
                    f"Rain expected in ~{hrs} hours. Pesticide wash-off will waste inputs and pollute waterways. "
                    f"Wait for a 24-hour dry window after rain before applying."
                ),
                'color': 'warning',
            }
        elif wind_speed >= 15:
            return {
                'status': 'high_wind',
                'title':  '🌬️ High Wind — Do Not Spray',
                'message': (
                    f"Wind speed {wind_speed:.0f} km/h exceeds safe spraying threshold (15 km/h). "
                    f"Drift risk is high. Wait for calm conditions, preferably early morning."
                ),
                'color': 'danger',
            }
        return {
            'status': 'monitor',
            'title':  '📊 Conditions Marginal',
            'message': 'Conditions are borderline. Check weather again before spraying. Prefer early morning windows.',
            'color': 'info',
        }

    def _get_daily_activities(self, weather: Dict) -> List[Dict]:
        temp        = weather.get('temperature', 25)
        humidity    = weather.get('humidity', 70)
        description = weather.get('description', '').lower()
        is_raining  = 'rain' in description

        activities = []
        if not is_raining and temp < 32:
            activities.append({'activity': 'Land Preparation / Tilling', 'icon': '🚜',
                                'priority': 'high', 'detail': f'Dry, {temp:.0f}°C. Good conditions for tractor or hand-tilling.'})
        if not is_raining and humidity < 65:
            activities.append({'activity': 'Harvest & Sun-Dry', 'icon': '☀️',
                                'priority': 'high', 'detail': f'Low humidity ({humidity:.0f}%). Ideal for harvesting and drying grains on tarpaulins.'})
        if is_raining or humidity > 80:
            activities.append({'activity': 'Skip Irrigation Today', 'icon': '💧',
                                'priority': 'medium', 'detail': 'Soil is saturated. Irrigating now causes waterlogging and root rot.'})
        if temp > 28 and not is_raining:
            activities.append({'activity': 'Weed Control', 'icon': '🌿',
                                'priority': 'medium', 'detail': f'Warm and dry ({temp:.0f}°C). Uprooted weeds will wilt and die quickly.'})
        if 'clear' in description or 'sun' in description:
            activities.append({'activity': 'Dry & Store Produce', 'icon': '🌤️',
                                'priority': 'high', 'detail': 'Clear sky. Spread harvested grain/coffee/simsim for solar drying.'})
        if is_raining:
            activities.append({'activity': 'Farm Record Keeping', 'icon': '📋',
                                'priority': 'low', 'detail': 'Use indoor time to update planting dates, input costs, and yields.'})
        return activities[:4]

    # ----------------------------------------------------------
    # API HELPERS
    # ----------------------------------------------------------

    def _get_forecast_cached(self, location: str) -> List[Dict]:
        """Fetch 5-day forecast, cached for 30 minutes to avoid duplicate API hits."""
        cache_key = f'weather_forecast_{location.lower().replace(" ", "_")}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        result = self._get_forecast(location)
        cache.set(cache_key, result, timeout=1800)  # 30 minutes
        return result

    def _get_forecast(self, location: str) -> List[Dict]:
        """Fetch raw forecast from OpenWeatherMap."""
        try:
            url    = f"{self.base_url}/forecast"
            params = {
                'q': f"{location},UG",
                'appid': self.api_key,
                'units': 'metric',
                'cnt': 40,
            }
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json().get('list', [])
        except Exception:
            pass
        return []

    def _check_rain_forecast(self, forecast: List[Dict], days: int = 3) -> bool:
        if not forecast:
            return False
        cutoff = datetime.now() + timedelta(days=days)
        for item in forecast:
            if datetime.fromtimestamp(item['dt']) > cutoff:
                break
            if 'rain' in item.get('weather', [{}])[0].get('main', '').lower():
                return True
        return False

    def _hours_until_rain(self, forecast: List[Dict]) -> int:
        for item in forecast:
            if 'rain' in item.get('weather', [{}])[0].get('main', '').lower():
                return max(0, int((datetime.fromtimestamp(item['dt']) - datetime.now()).total_seconds() / 3600))
        return 24
