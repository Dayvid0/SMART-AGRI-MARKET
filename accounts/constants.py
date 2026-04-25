# apps/accounts/constants.py — single source of truth for Uganda districts

UGANDA_REGIONS = {
    'Central': [
        'Buikwe', 'Bukomansimbi', 'Buvuma', 'Gomba', 'Kalangala',
        'Kalungu', 'Kampala', 'Kayunga', 'Kiboga', 'Kyankwanzi', 'Luweero',
        'Lwengo', 'Lyantonde', 'Masaka', 'Mityana', 'Mpigi', 'Mubende',
        'Mukono', 'Nakaseke', 'Nakasongola', 'Rakai', 'Sembabule', 'Wakiso',
    ],
    'Eastern': [
        'Amuria', 'Budaka', 'Bududa', 'Bugiri', 'Bugweri', 'Bukedea',
        'Bukwa', 'Bulambuli', 'Busia', 'Buyende', 'Iganga',
        'Jinja', 'Kaberamaido', 'Kaliro', 'Kamuli', 'Kapchorwa',
        'Katakwi', 'Kibuku', 'Kumi', 'Kween', 'Luuka', 'Manafwa',
        'Mayuge', 'Mbale', 'Namayingo', 'Namisindwa', 'Namutumba', 'Ngora',
        'Pallisa', 'Serere', 'Sironko', 'Soroti', 'Tororo',
    ],
    'Northern': [
        'Abim', 'Adjumani', 'Agago', 'Alebtong', 'Amolatar', 'Amudat',
        'Amuru', 'Apac', 'Arua', 'Dokolo', 'Gulu', 'Kaabong',
        'Kitgum', 'Koboko', 'Kole', 'Kotido', 'Kwania', 'Lamwo',
        'Lira', 'Maracha', 'Moroto', 'Moyo', 'Madi-Okollo', 'Nakapiripirit',
        'Napak', 'Nebbi', 'Nwoya', 'Obongi', 'Omoro', 'Otuke',
        'Oyam', 'Pader', 'Pakwach', 'Terego', 'Yumbe', 'Zombo',
    ],
    'Western': [
        'Buhweju', 'Buliisa', 'Bundibugyo', 'Bushenyi', 'Hoima',
        'Ibanda', 'Isingiro', 'Kabale', 'Kabarole', 'Kagadi', 'Kakumiro',
        'Kamwenge', 'Kanungu', 'Kasese', 'Kibaale', 'Kikuube', 'Kiruhura',
        'Kiryandongo', 'Kisoro', 'Kitagwenda', 'Kyegegwa', 'Kyenjojo',
        'Masindi', 'Mbarara', 'Mitooma', 'Ntoroko', 'Ntungamo',
        'Rubanda', 'Rubirizi', 'Rukiga', 'Rukungiri', 'Sheema', 'Rwampara',
    ],
}

DISTRICT_COORDINATES = {
    'Kampala':   {'lat': 0.3476,  'lng': 32.5825},
    'Wakiso':    {'lat': 0.3958,  'lng': 32.4786},
    'Mukono':    {'lat': 0.3544,  'lng': 32.7533},
    'Jinja':     {'lat': 0.4479,  'lng': 33.2026},
    'Masaka':    {'lat': -0.3411, 'lng': 31.7361},
    'Luweero':   {'lat': 0.8417,  'lng': 32.4930},
    'Mbarara':   {'lat': -0.6072, 'lng': 30.6545},
    'Gulu':      {'lat': 2.7724,  'lng': 32.2881},
    'Lira':      {'lat': 2.2479,  'lng': 32.8998},
    'Arua':      {'lat': 3.0303,  'lng': 30.9073},
    'Mbale':     {'lat': 1.0784,  'lng': 34.1750},
    'Soroti':    {'lat': 1.7146,  'lng': 33.6110},
    'Tororo':    {'lat': 0.6922,  'lng': 34.1808},
    'Kasese':    {'lat': 0.1764,  'lng': 30.0805},
    'Kabale':    {'lat': -1.2494, 'lng': 29.9880},
    'Hoima':     {'lat': 1.4331,  'lng': 31.3524},
    'Kapchorwa': {'lat': 1.3924,  'lng': 34.4503},
    'Moroto':    {'lat': 2.5369,  'lng': 34.6666},
}

ALL_DISTRICTS = sorted(set(d for districts in UGANDA_REGIONS.values() for d in districts))

DISTRICT_CHOICES = [(d, d) for d in ALL_DISTRICTS]

# Grouped optgroup choices for Django form rendering
UGANDA_DISTRICT_CHOICES = [
    (f'{region} Region', [(d, d) for d in sorted(districts)])
    for region, districts in UGANDA_REGIONS.items()
]

SPECIALIZATION_CHOICES = [
    (s, s) for s in [
        "Crop Farming", "Livestock Farming", "Poultry Farming",
        "Fish Farming (Aquaculture)", "Dairy Farming", "Horticulture",
        "Apiculture (Beekeeping)", "Mixed Farming", "Organic Farming",
        "Agricultural Extension", "Agribusiness", "Agricultural Research", "Other"
    ]
]
