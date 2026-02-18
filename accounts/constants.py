# apps/accounts/constants.py

UGANDA_DISTRICT_CHOICES = [
    ('Central Region', (
        ('Kampala', 'Kampala'), ('Wakiso', 'Wakiso'), ('Mpigi', 'Mpigi'),
        ('Mukono', 'Mukono'), ('Luwero', 'Luwero'), ('Nakasongola', 'Nakasongola'),
        ('Masaka', 'Masaka'), ('Rakai', 'Rakai'), ('Kalangala', 'Kalangala'),
        ('Lyantonde', 'Lyantonde'), ('Sembabule', 'Sembabule'), ('Bukomansimbi', 'Bukomansimbi'),
    )),
    ('Eastern Region', (
        ('Jinja', 'Jinja'), ('Iganga', 'Iganga'), ('Mayuge', 'Mayuge'),
        ('Bugiri', 'Bugiri'), ('Tororo', 'Tororo'), ('Busia', 'Busia'),
        ('Mbale', 'Mbale'), ('Bududa', 'Bududa'), ('Manafwa', 'Manafwa'),
        ('Sironko', 'Sironko'), ('Kapchorwa', 'Kapchorwa'), ('Kween', 'Kween'),
        ('Bukwo', 'Bukwo'), ('Soroti', 'Soroti'), ('Serere', 'Serere'),
        ('Kumi', 'Kumi'), ('Bukedea', 'Bukedea'),
    )),
    ('Northern Region', (
        ('Gulu', 'Gulu'), ('Kitgum', 'Kitgum'), ('Pader', 'Pader'),
        ('Agago', 'Agago'), ('Amuru', 'Amuru'), ('Nwoya', 'Nwoya'),
        ('Lamwo', 'Lamwo'), ('Lira', 'Lira'), ('Alebtong', 'Alebtong'),
        ('Apac', 'Apac'), ('Dokolo', 'Dokolo'), ('Oyam', 'Oyam'),
        ('Kole', 'Kole'), ('Otuke', 'Otuke'), ('Arua', 'Arua'),
        ('Koboko', 'Koboko'), ('Maracha', 'Maracha'), ('Yumbe', 'Yumbe'),
        ('Nebbi', 'Nebbi'), ('Zombo', 'Zombo'), ('Moyo', 'Moyo'),
    )),
    ('Western Region', (
        ('Mbarara', 'Mbarara'), ('Isingiro', 'Isingiro'), ('Kiruhura', 'Kiruhura'),
        ('Ntungamo', 'Ntungamo'), ('Kabale', 'Kabale'), ('Kisoro', 'Kisoro'),
        ('Rukungiri', 'Rukungiri'), ('Kanungu', 'Kanungu'), ('Kasese', 'Kasese'),
        ('Bundibugyo', 'Bundibugyo'), ('Kabarole', 'Kabarole'), ('Kyenjojo', 'Kyenjojo'),
        ('Bushenyi', 'Bushenyi'), ('Sheema', 'Sheema'), ('Mitooma', 'Mitooma'),
        ('Hoima', 'Hoima'), ('Masindi', 'Masindi'), ('Kiryandongo', 'Kiryandongo'),
    )),
]

SPECIALIZATION_CHOICES = [
    (s, s) for s in [
        "Crop Farming", "Livestock Farming", "Poultry Farming",
        "Fish Farming (Aquaculture)", "Dairy Farming", "Horticulture",
        "Apiculture (Beekeeping)", "Mixed Farming", "Organic Farming",
        "Agricultural Extension", "Agribusiness", "Agricultural Research", "Other"
    ]
]