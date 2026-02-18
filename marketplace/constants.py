"""
Constants for Uganda Districts, Regions, and Coordinates.
"""

UGANDA_REGIONS = {
    'Central': [
        'Kampala', 'Entebbe', 'Wakiso', 'Mukono', 'Masaka', 'Jinja', 'Luweero', 
        'Mpigi', 'Nakasongola', 'Rakai', 'Kalangala', 'Lyantonde', 'Sembabule', 'Bukomansimbi'
    ],
    'Western': [
        'Mbarara', 'Kasese', 'Fort Portal', 'Kabale', 'Hoima', 'Bushenyi', 
        'Isingiro', 'Kiruhura', 'Ntungamo', 'Kisoro', 'Rukungiri', 'Kanungu', 
        'Bundibugyo', 'Kabarole', 'Kyenjojo', 'Sheema', 'Mitooma', 'Masindi', 'Kiryandongo'
    ],
    'Eastern': [
        'Mbale', 'Soroti', 'Iganga', 'Tororo', 'Kumi', 'Jinja', 'Mayuge', 'Bugiri', 
        'Busia', 'Bududa', 'Manafwa', 'Sironko', 'Kapchorwa', 'Kween', 'Bukwo', 
        'Serere', 'Bukedea'
    ],
    'Northern': [
        'Gulu', 'Lira', 'Arua', 'Kitgum', 'Nebbi', 'Pader', 'Agago', 'Amuru', 
        'Nwoya', 'Lamwo', 'Alebtong', 'Apac', 'Dokolo', 'Oyam', 'Kole', 'Otuke', 
        'Koboko', 'Maracha', 'Yumbe', 'Zombo', 'Moyo'
    ]
}

# Approximate coordinates for mapping (Latitude, Longitude)
DISTRICT_COORDINATES = {
    'Kampala': {'lat': 0.3476, 'lng': 32.5825},
    'Entebbe': {'lat': 0.0512, 'lng': 32.4637},
    'Wakiso': {'lat': 0.3958, 'lng': 32.4786},
    'Mukono': {'lat': 0.3544, 'lng': 32.7533},
    'Jinja': {'lat': 0.4479, 'lng': 33.2026},
    'Masaka': {'lat': -0.3411, 'lng': 31.7361},
    'Mbarara': {'lat': -0.6072, 'lng': 30.6545},
    'Gulu': {'lat': 2.7724, 'lng': 32.2881},
    'Lira': {'lat': 2.2479, 'lng': 32.8998},
    'Arua': {'lat': 3.0303, 'lng': 30.9073},
    'Mbale': {'lat': 1.0784, 'lng': 34.1750},
    'Soroti': {'lat': 1.7146, 'lng': 33.6110},
    'Tororo': {'lat': 0.6922, 'lng': 34.1808},
    'Kasese': {'lat': 0.1764, 'lng': 30.0805},
    'Fort Portal': {'lat': 0.6726, 'lng': 30.2749},
    'Kabale': {'lat': -1.2494, 'lng': 29.9880},
    'Hoima': {'lat': 1.4331, 'lng': 31.3524},
    'Luweero': {'lat': 0.8417, 'lng': 32.4930},
    'Kapchorwa': {'lat': 1.3924, 'lng': 34.4503},
    'Moroto': {'lat': 2.5369, 'lng': 34.6666},
}

# Flattens the dictionary into a sorted list of unique districts
ALL_DISTRICTS = sorted(list(set(
    district for districts in UGANDA_REGIONS.values() for district in districts
)))

# Tuple choices for Django models
DISTRICT_CHOICES = [(d, d) for d in ALL_DISTRICTS]
