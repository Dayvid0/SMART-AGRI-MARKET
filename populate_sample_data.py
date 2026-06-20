"""
populate_sample_data.py — Full dataset for Smart Agri Market demo

Run:  python manage.py shell < populate_sample_data.py
  OR: python populate_sample_data.py

Creates:
  - 5 farmers (across different districts)
  - 2 consumers + 1 business buyer
  - 1 transporter with profile
  - 10 products across all categories
  - 25 crowdsourced market price reports
  - 4 official market prices
  - 2 completed orders with reviews (triggers rating signal)
  - 2 active group buy pools
  - Weather, pest, planting data
  - Agricultural inputs + news
"""

import os
import django
from datetime import date, timedelta, datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, FarmerProfile, InputSupplierProfile, TransporterProfile
from inputs.models import InputCategory, AgriculturalInput, GroupBuyPool, GroupBuyParticipant
from news.models import NewsCategory, AgriNews
from weather.models import WeatherAlert, PlantingSeason, PestAlert
from marketplace.models import (
    MarketPrice, Category, Product, CrowdsourcedPrice, Review, ReviewResponse
)
from orders.models import Order, OrderItem
from notifications.models import Notification
from django.utils import timezone

print("Starting full sample data population...\n")

# ===========================================================
# 1. MARKETPLACE CATEGORIES
# ===========================================================
print("1/10 Creating marketplace categories...")
categories_data = [
    ('Vegetables', 'Fresh vegetables including tomatoes, cabbage, onions, pepper'),
    ('Fruits', 'Fresh seasonal fruits: mangoes, jackfruit, passion fruit, avocado'),
    ('Cereals & Grains', 'Maize, beans, millet, sorghum, rice and other staples'),
    ('Cash Crops', 'Coffee, tea, cotton, sugarcane and other export crops'),
    ('Livestock & Poultry', 'Live animals, chicken, eggs, beef, pork, fish'),
]
cats = {}
for name, desc in categories_data:
    c, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
    cats[name] = c
    print(f"  -> {name}")

# ===========================================================
# 2. USERS
# ===========================================================
print("\n2/10 Creating users...")

def make_user(username, email, password, user_type, phone, location, district, first_name='', last_name=''):
    if User.objects.filter(username=username).exists():
        return User.objects.get(username=username)
    return User.objects.create_user(
        username=username, email=email, password=password,
        user_type=user_type, phone=phone, location=location,
        district=district, first_name=first_name, last_name=last_name
    )

# Farmers
farmers = []
farmer_data = [
    ('john_muyama',  'john@agrimarket.ug',    'Farmer@2024', '+256701234567', 'Mukono',    'Mukono',    'John',    'Muyama'),
    ('grace_akello', 'grace@agrimarket.ug',   'Farmer@2024', '+256702234567', 'Gulu',      'Gulu',      'Grace',   'Akello'),
    ('david_omara',  'david@agrimarket.ug',   'Farmer@2024', '+256703234567', 'Mbale',     'Mbale',     'David',   'Omara'),
    ('sarah_nakku',  'sarah@agrimarket.ug',   'Farmer@2024', '+256704234567', 'Masaka',    'Masaka',    'Sarah',   'Nakku'),
    ('moses_tukei',  'moses@agrimarket.ug',   'Farmer@2024', '+256705234567', 'Hoima',     'Hoima',     'Moses',   'Tukei'),
]
for uname, email, pwd, phone, loc, district, fn, ln in farmer_data:
    u = make_user(uname, email, pwd, 'farmer', phone, loc, district, fn, ln)
    farmers.append(u)
    fp, _ = FarmerProfile.objects.get_or_create(
        user=u,
        defaults={
            'farm_name': f'{fn} {ln} Farm',
            'farm_size': [5.5, 12.0, 8.0, 3.5, 20.0][farmers.index(u)],
            'specialization': ['Crop Farming', 'Crop Farming', 'Horticulture', 'Mixed Farming', 'Cash Crops'][farmers.index(u)],
        }
    )
    print(f"  Farmer: {uname}")

# Consumers
consumer1 = make_user('alice_buyer', 'alice@gmail.com', 'Consumer@2024', '+256706234567', 'Kampala', 'Kampala', 'Alice', 'Nakato', 'consumer')
consumer2 = make_user('kampala_resto', 'resto@gmail.com', 'Consumer@2024', '+256707234567', 'Kampala', 'Kampala', 'Kampala', 'Restaurant', 'business')
print("  Consumer: alice_buyer, kampala_resto")

# Transporter
transporter1 = make_user('boda_express', 'boda@agrimarket.ug', 'Transport@2024', '+256708234567', 'Kampala', 'Wakiso', 'Boda', 'Express', 'transporter')
TransporterProfile.objects.get_or_create(
    user=transporter1,
    defaults={
        'vehicle_type': 'pickup',
        'vehicle_registration': 'UAA 450B',
        'capacity_kg': 1500,
        'coverage_districts': 'Kampala,Wakiso,Mukono,Mpigi,Luweero,Masaka',
    }
)
print("  Transporter: boda_express")

# ===========================================================
# 3. PRODUCTS
# ===========================================================
print("\n3/10 Creating products...")
products_data = [
    {
        'farmer': farmers[0], 'category': cats['Vegetables'],
        'name': 'Fresh Tomatoes (Kampala Round)', 'price': 2500, 'quantity': 500, 'unit': 'kg',
        'location': 'Mukono', 'is_urgent': True, 'urgent_discount': 15,
        'harvest_date': date.today() - timedelta(days=2),
        'description': 'Freshly harvested round tomatoes, ready for market. No chemicals used in last 2 weeks.',
        'status': 'available',
    },
    {
        'farmer': farmers[0], 'category': cats['Vegetables'],
        'name': 'Sukuma Wiki (Kale)', 'price': 1200, 'quantity': 200, 'unit': 'bunches',
        'location': 'Mukono', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'Organically grown kale. Bunches of 8–10 stalks. Ideal for restaurants.',
        'status': 'available',
    },
    {
        'farmer': farmers[1], 'category': cats['Cereals & Grains'],
        'name': 'White Maize (Dry Grain)', 'price': 1800, 'quantity': 2000, 'unit': 'kg',
        'location': 'Gulu', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'High-quality dry maize grain from Northern Uganda. Moisture content below 14%. Suitable for milling.',
        'status': 'available',
    },
    {
        'farmer': farmers[1], 'category': cats['Cereals & Grains'],
        'name': 'Dried Beans (Nambale)', 'price': 3200, 'quantity': 800, 'unit': 'kg',
        'location': 'Gulu', 'is_urgent': True, 'urgent_discount': 10,
        'harvest_date': date.today() - timedelta(days=5),
        'description': 'Premium Nambale variety dry beans. Clean, sorted. Ideal for export or local supermarkets.',
        'status': 'available',
    },
    {
        'farmer': farmers[2], 'category': cats['Fruits'],
        'name': 'Ripe Mangoes (Julie Variety)', 'price': 800, 'quantity': 1500, 'unit': 'pieces',
        'location': 'Mbale', 'is_urgent': True, 'urgent_discount': 20,
        'harvest_date': date.today() - timedelta(days=1),
        'description': 'Sweet Julie mangoes from Eastern Uganda highlands. Peak season — buy now before they ripen further.',
        'status': 'available',
    },
    {
        'farmer': farmers[2], 'category': cats['Vegetables'],
        'name': 'Irish Potatoes (Victoria)', 'price': 1500, 'quantity': 1200, 'unit': 'kg',
        'location': 'Mbale', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'Victoria variety Irish potatoes from the slopes of Mt. Elgon. Excellent for chips and boiling.',
        'status': 'available',
    },
    {
        'farmer': farmers[3], 'category': cats['Fruits'],
        'name': 'Passion Fruit (Purple)', 'price': 1200, 'quantity': 600, 'unit': 'kg',
        'location': 'Masaka', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'Purple passion fruit, ripe and ready. High juice content. Popular with juice processors.',
        'status': 'available',
    },
    {
        'farmer': farmers[3], 'category': cats['Vegetables'],
        'name': 'Red Onions (Small Size)', 'price': 2200, 'quantity': 400, 'unit': 'kg',
        'location': 'Masaka', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'Red onions, cured and dried. Small size, ideal for retail. Grown without synthetic pesticides.',
        'status': 'available',
    },
    {
        'farmer': farmers[4], 'category': cats['Cash Crops'],
        'name': 'Robusta Coffee (Parchment)', 'price': 8500, 'quantity': 500, 'unit': 'kg',
        'location': 'Hoima', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'Premium Robusta parchment coffee from Western Uganda. Wet-processed. Suitable for UCDA certification.',
        'status': 'available',
    },
    {
        'farmer': farmers[4], 'category': cats['Livestock & Poultry'],
        'name': 'Local Eggs (Free Range)', 'price': 450, 'quantity': 2000, 'unit': 'pieces',
        'location': 'Hoima', 'is_urgent': False, 'urgent_discount': 0,
        'description': 'Fresh free-range eggs from local hens fed on natural grain. Available in trays of 30.',
        'status': 'available',
    },
]

products = []
for pd in products_data:
    harvest = pd.pop('harvest_date', None)
    p, created = Product.objects.get_or_create(
        farmer=pd['farmer'], name=pd['name'],
        defaults={**pd, 'harvest_date': harvest}
    )
    products.append(p)
    if created:
        print(f"  -> {p.name}")

# ===========================================================
# 4. CROWDSOURCED MARKET PRICES
# ===========================================================
print("\n4/10 Creating crowdsourced price reports...")
price_reports = [
    ('Tomatoes', 2500, 'kg', 'middleman', 'Kampala', 'Nakasero Market'),
    ('Tomatoes', 3200, 'kg', 'direct_consumer', 'Kampala', 'Owino Market'),
    ('Tomatoes', 2200, 'kg', 'middleman', 'Wakiso', 'Kasangati Market'),
    ('Maize', 1800, 'kg', 'middleman', 'Gulu', 'Gulu Main Market'),
    ('Maize', 2100, 'kg', 'business', 'Kampala', 'Nakawa Market'),
    ('Maize', 1650, 'kg', 'middleman', 'Lira', 'Lira Market'),
    ('Beans', 3000, 'kg', 'middleman', 'Mbale', 'Mbale Market'),
    ('Beans', 3500, 'kg', 'direct_consumer', 'Kampala', 'Nakasero'),
    ('Beans', 2800, 'kg', 'market', 'Jinja', 'Jinja Main Market'),
    ('Coffee', 8000, 'kg', 'middleman', 'Hoima', 'Hoima Town'),
    ('Coffee', 9000, 'kg', 'business', 'Kampala', 'NUCAFE Collection Centre'),
    ('Onions', 2000, 'kg', 'middleman', 'Masaka', 'Masaka Market'),
    ('Onions', 2500, 'kg', 'direct_consumer', 'Kampala', 'City Market'),
    ('Potatoes', 1400, 'kg', 'middleman', 'Mbale', 'Mbale Market'),
    ('Potatoes', 1800, 'kg', 'business', 'Kampala', 'Nakasero'),
    ('Mangoes', 700, 'pieces', 'middleman', 'Mbale', 'Mbale Market'),
    ('Mangoes', 900, 'pieces', 'direct_consumer', 'Kampala', 'City Market'),
    ('Eggs', 400, 'pieces', 'direct_consumer', 'Hoima', 'Hoima Market'),
    ('Eggs', 450, 'pieces', 'business', 'Kampala', 'Supermarket'),
    ('Passion Fruit', 1100, 'kg', 'middleman', 'Masaka', 'Masaka Market'),
    ('Kale (Sukuma Wiki)', 1000, 'bunches', 'direct_consumer', 'Kampala', 'Nakasero'),
    ('Groundnuts', 4500, 'kg', 'middleman', 'Arua', 'Arua Market'),
    ('Sweet Potatoes', 900, 'kg', 'middleman', 'Luwero', 'Luwero Market'),
    ('Cassava', 600, 'kg', 'middleman', 'Masaka', 'Masaka Market'),
    ('Rice', 3800, 'kg', 'business', 'Kampala', 'Nakasero Rice Dealers'),
]

reporters = farmers + [consumer1]
for i, (product_name, price, unit, buyer_type, location, market_name) in enumerate(price_reports):
    CrowdsourcedPrice.objects.get_or_create(
        reporter=reporters[i % len(reporters)],
        product_name=product_name,
        price=price,
        location=location,
        defaults={
            'unit': unit,
            'buyer_type': buyer_type,
            'market_name': market_name,
            'is_verified': i < 10,  # first 10 are "verified" by admin
        }
    )
print(f"  -> {len(price_reports)} crowdsourced reports")

# ===========================================================
# 5. OFFICIAL MARKET PRICES
# ===========================================================
print("\n5/10 Creating official market prices...")
official_prices = [
    ('Maize (White)', cats['Cereals & Grains'], 'Owino Market, Kampala', 1600, 2200, 1900),
    ('Dry Beans', cats['Cereals & Grains'], 'Nakasero Market, Kampala', 2800, 3800, 3200),
    ('Tomatoes', cats['Vegetables'], 'Nakasero Market, Kampala', 2000, 3500, 2600),
    ('Robusta Coffee', cats['Cash Crops'], 'NUCAFE Kampala', 7500, 9500, 8400),
]
for pname, cat, market, min_p, max_p, avg_p in official_prices:
    MarketPrice.objects.get_or_create(
        product_name=pname, market_location=market,
        defaults={
            'category': cat, 'min_price': min_p, 'max_price': max_p,
            'average_price': avg_p, 'unit': 'kg',
            'source': 'MAAIF/Nakasero Market Survey'
        }
    )
print("  -> 4 official market prices")

# ===========================================================
# 6. ORDERS + ORDER ITEMS
# ===========================================================
print("\n6/10 Creating sample orders...")
import random, string

def order_no():
    return 'ORD-' + datetime.now().strftime('%Y%m%d') + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# Completed order 1 — buyer: alice, farmer: john
if not Order.objects.filter(buyer=consumer1, farmer=farmers[0]).exists():
    o1 = Order.objects.create(
        buyer=consumer1, farmer=farmers[0],
        order_number=order_no(), status='completed',
        total_amount=75000,
        delivery_address='Plot 12, Kampala Road, Kampala',
        delivery_phone='+256706234567',
        notes='Please deliver before noon.'
    )
    OrderItem.objects.create(order=o1, product=products[0], quantity=30, unit_price=2500)
    print("  -> Order 1 (completed): alice -> john_muyama")

    # Review for order 1
    if not hasattr(o1, 'marketplace_review'):
        review1 = Review.objects.create(
            reviewer=consumer1, farmer=farmers[0], order=o1,
            rating=5, comment='Excellent tomatoes! Very fresh and good size. Delivered on time.',
            product_quality=5, communication=5, delivery_speed=4, would_recommend=True
        )
        ReviewResponse.objects.create(
            review=review1,
            response_text='Thank you so much Alice! We look forward to supplying you regularly.'
        )
        print("  -> Review + response added for Order 1")

# Completed order 2 — buyer: restaurant, farmer: grace
if not Order.objects.filter(buyer=consumer2, farmer=farmers[1]).exists():
    o2 = Order.objects.create(
        buyer=consumer2, farmer=farmers[1],
        order_number=order_no(), status='completed',
        total_amount=180000,
        delivery_address='Garden City Restaurant, Yusuf Lule Road',
        delivery_phone='+256707234567',
        notes='Bulk order for restaurant. Need delivery twice a week.'
    )
    OrderItem.objects.create(order=o2, product=products[2], quantity=100, unit_price=1800)
    print("  -> Order 2 (completed): kampala_resto -> grace_akello")

    review2 = Review.objects.create(
        reviewer=consumer2, farmer=farmers[1], order=o2,
        rating=4, comment='Good quality maize grain. Will order again next month.',
        product_quality=4, communication=4, delivery_speed=3, would_recommend=True
    )
    print("  -> Review added for Order 2")

# Pending order
if not Order.objects.filter(buyer=consumer1, farmer=farmers[2]).exists():
    o3 = Order.objects.create(
        buyer=consumer1, farmer=farmers[2],
        order_number=order_no(), status='pending',
        total_amount=24000,
        delivery_address='Nakasero, Kampala',
        delivery_phone='+256706234567',
    )
    OrderItem.objects.create(order=o3, product=products[4], quantity=30, unit_price=800)
    print("  -> Order 3 (pending): alice -> david_omara")

# ===========================================================
# 7. INPUT SUPPLIER + INPUTS
# ===========================================================
print("\n7/10 Input supplier already exists — checking inputs...")
if not User.objects.filter(username='supplier1').exists():
    supplier = User.objects.create_user(
        username='supplier1', email='supplier@agrimarket.ug', password='Supplier@2024',
        user_type='input_supplier', location='Kampala', phone='+256700111222'
    )
    InputSupplierProfile.objects.create(
        user=supplier, company_name='AgriSupplies Uganda Ltd',
        specialization='Seeds, Fertilizers, and Pesticides',
        business_license='UG-AS-2024-001'
    )
else:
    supplier = User.objects.get(username='supplier1')

seed_cat, _ = InputCategory.objects.get_or_create(name='Improved Seeds', defaults={'category_type': 'seeds'})
fert_cat, _ = InputCategory.objects.get_or_create(name='Organic Fertilizers', defaults={'category_type': 'fertilizers'})

# Add more inputs
extra_inputs = [
    {
        'name': 'Beans Seed (Nambale K132)',
        'category': seed_cat, 'brand': 'NARO Uganda',
        'description': 'Disease-resistant Nambale K132 bean variety. Certified by NARO. 90-day maturity.',
        'price': 38000, 'quantity_available': 300, 'unit': 'kg',
        'min_group_order': 20, 'group_discount_percentage': 12,
    },
    {
        'name': 'Calcium Ammonium Nitrate (CAN)',
        'category': fert_cat, 'brand': 'UFZA',
        'description': 'Nitrogen fertilizer for top-dressing. 26% N. Best applied 3-4 weeks after planting.',
        'price': 95000, 'quantity_available': 150, 'unit': 'bags',
        'min_group_order': 5, 'group_discount_percentage': 8,
        'safety_warnings': 'Store away from heat. Do not mix with organic materials.',
    },
]
for inp in extra_inputs:
    AgriculturalInput.objects.get_or_create(supplier=supplier, name=inp['name'], defaults=inp)
    print(f"  -> Input: {inp['name']}")

# ===========================================================
# 8. GROUP BUY POOLS
# ===========================================================
print("\n8/10 Creating group buy pools...")
try:
    seed_input = AgriculturalInput.objects.filter(supplier=supplier, category=seed_cat).first()
    fert_input = AgriculturalInput.objects.filter(supplier=supplier, category=fert_cat).first()

    if seed_input and not GroupBuyPool.objects.filter(input_item=seed_input, organizer=farmers[0]).exists():
        pool1 = GroupBuyPool.objects.create(
            input_item=seed_input, organizer=farmers[0],
            target_quantity=200, current_quantity=55,
            deadline=timezone.now() + timedelta(days=10), status='open'
        )
        GroupBuyParticipant.objects.get_or_create(pool=pool1, farmer=farmers[0], defaults={'quantity': 30})
        GroupBuyParticipant.objects.get_or_create(pool=pool1, farmer=farmers[1], defaults={'quantity': 25})
        print(f"  -> Pool 1: {seed_input.name} (55/200)")

    if fert_input and not GroupBuyPool.objects.filter(input_item=fert_input, organizer=farmers[2]).exists():
        pool2 = GroupBuyPool.objects.create(
            input_item=fert_input, organizer=farmers[2],
            target_quantity=50, current_quantity=50,
            deadline=timezone.now() + timedelta(days=3), status='closed'
        )
        for farmer in farmers[:3]:
            GroupBuyParticipant.objects.get_or_create(pool=pool2, farmer=farmer, defaults={'quantity': round(50/3)})
        print(f"  -> Pool 2: {fert_input.name} (CLOSED — target reached)")
except Exception as e:
    print(f"  Group buy pools error: {e}")

# ===========================================================
# 9. WEATHER, PEST, PLANTING DATA
# ===========================================================
print("\n9/10 Weather + Pest + Planting data...")
if not WeatherAlert.objects.filter(is_active=True).exists():
    WeatherAlert.objects.create(
        alert_type='rain', severity='medium',
        title='Heavy Rainfall Expected — Central Region',
        description='UNMA forecasts 90–130mm of rainfall across Central Uganda from June 18–25, 2026.',
        affected_regions='Kampala, Wakiso, Mukono, Mpigi, Luwero, Masaka, Masaka',
        start_date=timezone.now(), end_date=timezone.now() + timedelta(days=7),
        recommendations='1. Harvest mature crops before rains.\n2. Ensure drainage channels are clear.\n3. Protect stored grain from moisture.\n4. Delay planting on waterlogged soils.',
        is_active=True,
    )
    print("  -> Weather alert")

for season_data in [
    {'crop_name': 'Maize', 'region': 'Central Region', 'best_planting_start': date(2026, 8, 1), 'best_planting_end': date(2026, 9, 30), 'expected_harvest_start': date(2026, 11, 1), 'expected_harvest_end': date(2026, 12, 31), 'rainfall_required': '800-1200mm', 'temperature_range': '20-30°C', 'planting_tips': 'Plant in rows 75cm apart, 25cm spacing. Apply basal fertilizer at planting.'},
    {'crop_name': 'Coffee (Robusta)', 'region': 'Central & Western', 'best_planting_start': date(2026, 3, 15), 'best_planting_end': date(2026, 5, 31), 'expected_harvest_start': date(2027, 8, 1), 'expected_harvest_end': date(2027, 12, 31), 'rainfall_required': '1000-2000mm', 'temperature_range': '18-25°C', 'planting_tips': 'Space plants 2.5m × 2.5m. Dig 60cm holes. Provide shade in year 1.'},
    {'crop_name': 'Beans', 'region': 'All Regions', 'best_planting_start': date(2026, 8, 1), 'best_planting_end': date(2026, 9, 15), 'expected_harvest_start': date(2026, 11, 1), 'expected_harvest_end': date(2026, 12, 15), 'rainfall_required': '400-600mm', 'temperature_range': '18-24°C', 'planting_tips': 'Plant rows 45cm apart. Intercrop with maize. Apply phosphate fertilizer at planting.'},
]:
    PlantingSeason.objects.get_or_create(crop_name=season_data['crop_name'], region=season_data['region'], defaults=season_data)
    print(f"  -> Planting season: {season_data['crop_name']}")

for pest_data in [
    {
        'pest_name': 'Fall Armyworm (Spodoptera frugiperda)',
        'affected_crops': 'Maize, Sorghum, Rice, Wheat',
        'affected_regions': 'Nationwide — all regions',
        'description': 'Invasive caterpillar pest that causes 20–70% yield loss in maize if uncontrolled.',
        'symptoms': 'Small holes in young leaves, damaged growing points, dark caterpillars (4cm), sawdust-like frass near plant whorls.',
        'severity': 'high',
        'control_measures': '1. Scout 2-3x/week\n2. Hand-pick young larvae\n3. Apply neem-based organic pesticide\n4. Use Bt products\n5. Chemical: Emamectin benzoate (last resort)',
        'is_active': True,
    },
    {
        'pest_name': 'Banana Weevil (Cosmopolites sordidus)',
        'affected_crops': 'Banana, Plantain',
        'affected_regions': 'Central, Western, Eastern regions',
        'description': 'Destroys banana corms and pseudostems. Major cause of banana plantation decline.',
        'symptoms': 'Yellowing leaves, weak pseudostems, tunnels visible in cut stems, reduced bunch size.',
        'severity': 'medium',
        'control_measures': '1. Use clean tissue-culture planting material\n2. Set pseudostem traps weekly\n3. Apply neem around plant base\n4. Remove and destroy badly infested plants',
        'is_active': True,
    },
]:
    PestAlert.objects.get_or_create(pest_name=pest_data['pest_name'], defaults=pest_data)
    print(f"  -> Pest alert: {pest_data['pest_name']}")

# ===========================================================
# 10. NEWS
# ===========================================================
print("\n10/10 Checking news articles...")
news_cat_market, _ = NewsCategory.objects.get_or_create(name='Market News')
news_cat_policy, _ = NewsCategory.objects.get_or_create(name='Policy Updates')
news_cat_tech, _ = NewsCategory.objects.get_or_create(name='Technology')
news_cat_events, _ = NewsCategory.objects.get_or_create(name='Training Events')

news_items = [
    {'title': 'Uganda Government Announces UGX 50B Agricultural Subsidy', 'news_type': 'government', 'summary': 'Ministry of Agriculture launches support program for smallholder farmers', 'content': 'Full details of the UGX 50 billion program available at district agricultural offices...', 'source': 'Ministry of Agriculture', 'is_featured': True, 'status': 'published', 'category': news_cat_policy},
    {'title': 'Coffee Prices Hit 5-Year High on International Markets', 'news_type': 'market', 'summary': 'Ugandan coffee farmers benefit from surge in global coffee prices', 'content': 'International coffee prices have reached highest in five years due to reduced Brazil production...', 'source': 'Uganda Coffee Development Authority', 'is_featured': True, 'status': 'published', 'category': news_cat_market},
    {'title': 'AI App Helps Farmers Identify Crop Diseases Instantly', 'news_type': 'technology', 'summary': 'New mobile app provides instant AI diagnosis and treatment', 'content': 'A new AI-powered app allows farmers to photograph affected crops for instant diagnosis...', 'source': 'AgriTech Uganda', 'status': 'published', 'category': news_cat_tech},
    {'title': 'Free Training: Modern Farming Techniques — Register Now', 'news_type': 'event', 'summary': 'NAADS announces countrywide free training sessions', 'content': 'NAADS training sessions cover improved varieties, pest management, post-harvest handling...', 'source': 'NAADS', 'is_urgent': True, 'status': 'published', 'category': news_cat_events},
]
for n in news_items:
    AgriNews.objects.get_or_create(title=n['title'], defaults=n)
    print(f"  -> News: {n['title'][:50]}")

# ===========================================================
# SUMMARY
# ===========================================================
print("\n" + "="*60)
print("SAMPLE DATA POPULATION COMPLETE")
print("="*60)
print(f"Users:              {User.objects.count()}")
print(f"Products:           {Product.objects.count()}")
print(f"Orders:             {Order.objects.count()}")
print(f"Reviews:            {Review.objects.count()}")
print(f"Crowdsourced Prices:{CrowdsourcedPrice.objects.count()}")
print(f"External Prices:    {__import__('marketplace.models', fromlist=['ExternalMarketPrice']).ExternalMarketPrice.objects.count()}")
print(f"Group Buy Pools:    {GroupBuyPool.objects.count()}")
print(f"News Articles:      {AgriNews.objects.count()}")
print(f"Pest Alerts:        {PestAlert.objects.count()}")
print(f"Weather Alerts:     {WeatherAlert.objects.count()}")
print("\nTest Credentials:")
print("  admin        / (create with: python manage.py createsuperuser)")
print("  john_muyama  / Farmer@2024    [Farmer — Mukono]")
print("  grace_akello / Farmer@2024    [Farmer — Gulu]")
print("  alice_buyer  / Consumer@2024  [Consumer — Kampala]")
print("  boda_express / Transport@2024 [Transporter — Wakiso]")
print("  supplier1    / test1234       [Input Supplier]")
print("="*60)

if __name__ == '__main__':
    pass