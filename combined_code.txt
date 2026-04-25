import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, InputSupplierProfile
from inputs.models import InputCategory, AgriculturalInput
from news.models import NewsCategory, AgriNews
from weather.models import WeatherAlert, PlantingSeason, PestAlert
from marketplace.models import MarketPrice, Category
from datetime import datetime, timedelta

def create_sample_data():
    print("🌱 Creating sample data for Smart Agricultural Marketplace...\n")
    
    # Create Input Supplier
    print("Creating input supplier...")
    if not User.objects.filter(username='supplier1').exists():
        supplier = User.objects.create_user(
            username='supplier1',
            email='supplier@agrimarket.ug',
            password='test1234',
            user_type='input_supplier',
            location='Kampala',
            phone='+256700111222',
            whatsapp_number='+256700111222'
        )
        
        InputSupplierProfile.objects.create(
            user=supplier,
            company_name='AgriSupplies Uganda Ltd',
            specialization='Seeds, Fertilizers, and Pesticides',
            business_license='UG-AS-2024-001'
        )
        print("✓ Created input supplier: supplier1")
    
    # Create Input Categories
    print("\nCreating input categories...")
    input_categories = [
        ('Improved Seeds', 'seeds'),
        ('Organic Fertilizers', 'fertilizers'),
        ('Pesticides', 'pesticides'),
        ('Herbicides', 'herbicides'),
        ('Farming Tools', 'tools'),
    ]
    
    for name, cat_type in input_categories:
        InputCategory.objects.get_or_create(
            name=name,
            defaults={'category_type': cat_type}
        )
        print(f"✓ {name}")
    
    # Create Sample Inputs
    print("\nCreating sample agricultural inputs...")
    try:
        supplier = User.objects.get(username='supplier1')
        seed_cat = InputCategory.objects.get(name='Improved Seeds')
        fert_cat = InputCategory.objects.get(name='Organic Fertilizers')
        pest_cat = InputCategory.objects.get(name='Pesticides')
        
        inputs_data = [
            {
                'name': 'Hybrid Maize Seeds (Premium)',
                'category': seed_cat,
                'brand': 'UgandaSeed',
                'description': 'High-yield hybrid maize seeds resistant to common diseases. Suitable for all regions of Uganda.',
                'price': 45000,
                'quantity_available': 500,
                'unit': 'kg',
                'min_group_order': 50,
                'group_discount_percentage': 15,
                'manufacturer': 'Uganda Seed Company',
            },
            {
                'name': 'NPK Fertilizer 17-17-17',
                'category': fert_cat,
                'brand': 'FertilePlus',
                'description': 'Balanced NPK fertilizer suitable for all types of crops. Enhances soil fertility and crop productivity.',
                'price': 120000,
                'quantity_available': 200,
                'unit': 'bags',
                'min_group_order': 10,
                'group_discount_percentage': 20,
                'usage_instructions': 'Apply 2-3 bags per acre during planting. For best results, mix with organic manure.',
                'safety_warnings': 'Store in a cool, dry place. Keep away from children and pets. Wear gloves when handling.',
            },
            {
                'name': 'Organic Pesticide - Bio Control',
                'category': pest_cat,
                'brand': 'EcoFarm',
                'description': 'Organic pesticide safe for vegetables and fruits. Effective against aphids, whiteflies, and caterpillars.',
                'price': 35000,
                'quantity_available': 100,
                'unit': 'liters',
                'min_group_order': 20,
                'group_discount_percentage': 10,
                'usage_instructions': 'Mix 50ml per 20 liters of water. Spray early morning or late evening.',
                'safety_warnings': 'Wear protective gear during application. Do not spray during windy conditions.',
            },
        ]
        
        for data in inputs_data:
            AgriculturalInput.objects.get_or_create(
                supplier=supplier,
                name=data['name'],
                defaults=data
            )
            print(f"✓ {data['name']}")
    except Exception as e:
        print(f"Error creating inputs: {e}")
    
    # Create News Categories
    print("\nCreating news categories...")
    news_cats = ['Policy Updates', 'Market News', 'Technology', 'Training Events', 'Weather Alerts']
    for cat_name in news_cats:
        NewsCategory.objects.get_or_create(name=cat_name)
        print(f"✓ {cat_name}")
    
    # Create Sample News
    print("\nCreating sample news articles...")
    news_data = [
        {
            'title': 'Government Announces UGX 50B Agricultural Subsidy Program',
            'news_type': 'government',
            'summary': 'Ministry of Agriculture unveils comprehensive support program for smallholder farmers',
            'content': '''The Ministry of Agriculture has launched a UGX 50 billion support program aimed at empowering smallholder farmers across Uganda. 
            
The program includes:
- Subsidized inputs (seeds and fertilizers)
- Access to low-interest agricultural loans
- Free training on modern farming techniques
- Market linkage support

Farmers can apply through their respective district agricultural offices starting March 1st, 2025. Priority will be given to organized farmer groups and cooperatives.

For more information, contact your nearest agricultural extension office or visit the Ministry's website.''',
            'source': 'Ministry of Agriculture, Animal Industry and Fisheries',
            'is_featured': True,
        },
        {
            'title': 'Coffee Prices Hit 5-Year High in International Markets',
            'news_type': 'market',
            'summary': 'Ugandan coffee farmers to benefit from surge in global coffee prices',
            'content': '''International coffee prices have reached their highest point in five years, offering great opportunities for Ugandan coffee farmers.
            
The price increase is attributed to:
- Reduced production in Brazil due to drought
- Increasing global demand for specialty coffee
- Strong quality reputation of Ugandan robusta and arabica coffee

Farmers are advised to maintain quality standards to maximize benefits from the price surge. Proper harvesting, processing, and storage practices will ensure premium prices.

The Uganda Coffee Development Authority encourages farmers to sell through certified cooperatives to get better prices.''',
            'source': 'Uganda Coffee Development Authority',
            'is_featured': True,
        },
        {
            'title': 'New Mobile App Helps Farmers Identify Crop Diseases',
            'news_type': 'technology',
            'summary': 'AI-powered app provides instant diagnosis and treatment recommendations',
            'content': '''A new mobile application using artificial intelligence is helping Ugandan farmers quickly identify and treat crop diseases.
            
Features include:
- Take a photo of the affected crop
- Instant AI-powered diagnosis
- Treatment recommendations with local pesticide options
- Connection to agricultural extension officers
- Community forum for farmers

The app is free to download from Google Play Store and works offline after initial setup. Over 50,000 farmers have already downloaded the app with positive feedback.''',
            'source': 'AgriTech Uganda',
        },
        {
            'title': 'Free Training on Modern Farming Techniques - Register Now',
            'news_type': 'event',
            'summary': 'National Agricultural Advisory Services announces countrywide training program',
            'content': '''NAADS is organizing free training sessions on modern farming techniques across all districts in Uganda.

Training Topics:
- Improved crop varieties and their management
- Integrated pest management
- Post-harvest handling and storage
- Value addition techniques
- Record keeping and farm business management

Training will run from March to May 2025. Register at your nearest NAADS office or call the toll-free number: 0800-100-200.''',
            'source': 'National Agricultural Advisory Services',
            'is_urgent': True,
        },
    ]
    
    for news in news_data:
        AgriNews.objects.get_or_create(
            title=news['title'],
            defaults=news
        )
        print(f"✓ {news['title'][:50]}...")
    
    # Create Weather Alert
    print("\nCreating weather alerts...")
    if not WeatherAlert.objects.filter(is_active=True).exists():
        WeatherAlert.objects.create(
            alert_type='rain',
            severity='medium',
            title='Heavy Rainfall Expected This Week',
            description='The meteorological department forecasts heavy rains across the central region from February 12-18, 2025. Expect 80-120mm of rainfall.',
            affected_regions='Kampala, Wakiso, Mukono, Mpigi, Luwero, Masaka',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            recommendations='''1. Harvest mature crops before the heavy rains start
2. Ensure proper drainage in your fields to prevent waterlogging
3. Protect harvested produce from moisture to avoid post-harvest losses
4. Delay planting if soil is already waterlogged
5. Check for weak structures and reinforce them''',
            is_active=True,
        )
        print("✓ Weather alert created")
    
    # Create Planting Seasons
    print("\nCreating planting season recommendations...")
    seasons = [
        {
            'crop_name': 'Maize',
            'region': 'Central Region',
            'best_planting_start': datetime(2025, 3, 1),
            'best_planting_end': datetime(2025, 4, 30),
            'expected_harvest_start': datetime(2025, 7, 1),
            'expected_harvest_end': datetime(2025, 8, 31),
            'rainfall_required': '800-1200mm',
            'temperature_range': '20-30°C',
            'planting_tips': 'Plant in rows 75cm apart with 25cm spacing between plants. Apply basal fertilizer at planting (1 tablespoon per hole) and top-dress with nitrogen after 3 weeks. Weed regularly and control pests.',
        },
        {
            'crop_name': 'Coffee (Robusta)',
            'region': 'Central & Western',
            'best_planting_start': datetime(2025, 3, 15),
            'best_planting_end': datetime(2025, 5, 31),
            'expected_harvest_start': datetime(2026, 8, 1),
            'expected_harvest_end': datetime(2026, 12, 31),
            'rainfall_required': '1000-2000mm',
            'temperature_range': '18-25°C',
            'planting_tips': 'Space plants 2.5m x 2.5m. Dig holes 60cm x 60cm x 60cm. Mix topsoil with manure before planting. Provide shade (banana plants) in the first year. Mulch heavily.',
        },
        {
            'crop_name': 'Beans',
            'region': 'All Regions',
            'best_planting_start': datetime(2025, 3, 1),
            'best_planting_end': datetime(2025, 4, 15),
            'expected_harvest_start': datetime(2025, 6, 1),
            'expected_harvest_end': datetime(2025, 7, 15),
            'rainfall_required': '400-600mm',
            'temperature_range': '18-24°C',
            'planting_tips': 'Plant in rows 45cm apart with 10cm spacing. Can be intercropped with maize. Apply phosphate fertilizer at planting. Harvest when pods turn brown and dry.',
        },
    ]
    
    for season in seasons:
        PlantingSeason.objects.get_or_create(
            crop_name=season['crop_name'],
            region=season['region'],
            defaults=season
        )
        print(f"✓ {season['crop_name']} planting season")
    
    # Create Pest Alerts
    print("\nCreating pest alerts...")
    pests = [
        {
            'pest_name': 'Fall Armyworm (Spodoptera frugiperda)',
            'affected_crops': 'Maize, Sorghum, Rice, Wheat',
            'affected_regions': 'Nationwide outbreak - All regions affected',
            'description': 'Fall armyworm is an invasive pest that has caused significant damage to cereal crops across Uganda. The larvae feed on leaves, stems, and reproductive parts of plants, causing substantial yield losses if not controlled.',
            'symptoms': '''Look for these signs:
- Small holes in young leaves (window paning)
- Damaged growing points and tassels
- Presence of dark green to brown caterpillars (up to 4cm long)
- Sawdust-like frass (excrement) near feeding sites
- Plants may appear ragged with large sections of leaves missing
- In severe cases, complete defoliation of plants''',
            'severity': 'high',
            'control_measures': '''Integrated Pest Management Approach:

1. Early Detection:
   - Scout fields regularly (at least 2-3 times per week)
   - Check plants in early morning when larvae are most active
   - Focus on whorl of young plants

2. Cultural Control:
   - Practice crop rotation
   - Intercrop with legumes or other non-host crops
   - Remove and destroy affected plant parts
   - Hand-pick and destroy egg masses and young larvae

3. Biological Control:
   - Use Bacillus thuringiensis (Bt) based products
   - Apply neem-based products (neem oil or neem cake)
   - Encourage natural predators (birds, wasps, beetles)

4. Chemical Control (if infestation is severe):
   - Apply approved pesticides during early morning or late evening
   - Target young larvae (stages 1-3) for best results
   - Rotate different classes of pesticides to prevent resistance
   - Follow label instructions carefully

5. Preventive Measures:
   - Plant early to avoid peak infestation periods
   - Use pest-resistant varieties when available
   - Maintain field hygiene''',
            'recommended_products': '''1. Bio-pesticides:
   - Bacillus thuringiensis (Bt) products
   - Neem-based products (Azadirachtin)
   
2. Chemical pesticides (use as last resort):
   - Emamectin benzoate
   - Chlorantraniliprole
   - Spinetoram
   
Note: Always consult agricultural extension officers before application.''',
            'is_active': True,
        },
        {
            'pest_name': 'Banana Weevil (Cosmopolites sordidus)',
            'affected_crops': 'Banana, Plantain, Enset',
            'affected_regions': 'Central, Western, Eastern, and Southwestern regions',
            'description': 'Banana weevil is one of the most destructive pests of banana in Uganda. Adult weevils bore into the pseudostem and corm, while larvae tunnel extensively, weakening plants and causing significant yield reductions.',
            'symptoms': '''Identification signs:
- Yellowing and wilting of leaves
- Weak, thin pseudostems
- Visible tunnels in the pseudostem when cut open
- Reduced bunch size and delayed maturity
- Plant toppling, especially when bearing fruit
- Dark adult weevils (about 12mm long) hiding in leaf sheaths
- Rotting of the corm with characteristic smell''',
            'severity': 'medium',
            'control_measures': '''Management Strategy:

1. Cultural Practices:
   - Use clean, certified planting materials (tissue culture)
   - Inspect all planting materials before planting
   - Practice proper field sanitation
   - Remove and destroy badly infested plants
   - Trim suckers before planting to remove eggs and larvae
   - Mulch heavily around plants

2. Trapping:
   - Use pseudostem traps: cut and split banana stems, place face down
   - Check traps weekly and destroy collected weevils
   - Use pheromone traps where available

3. Biological Control:
   - Apply neem-based products around the base of plants
   - Encourage natural enemies (ants, beetles)
   - Use entomopathogenic fungi if available

4. Chemical Control:
   - Apply recommended insecticides at planting
   - Treat suckers before transplanting
   - Apply nematicides if nematodes are also present

5. Prevention:
   - Rotate planting areas when possible
   - Remove dead leaves and plant debris
   - Avoid wounding plants during weeding
   - Plant in well-drained soils''',
            'recommended_products': '''1. Organic options:
   - Neem oil or neem cake
   - Wood ash application around base
   
2. Biological:
   - Beauveria bassiana (fungal biocontrol)
   - Pheromone traps
   
3. Chemical (if necessary):
   - Contact your agricultural extension officer for approved products
   
Always follow integrated pest management principles.''',
            'is_active': True,
        },
    ]
    
    for pest in pests:
        PestAlert.objects.get_or_create(
            pest_name=pest['pest_name'],
            defaults=pest
        )
        print(f"✓ {pest['pest_name']} alert")
    
    print("\n" + "="*60)
    print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print("\n📝 Test Credentials:")
    print("   Input Supplier Account:")
    print("   Username: supplier1")
    print("   Password: test1234")
    print("\n🌐 You can now explore:")
    print("   ✓ Input Store with sample products")
    print("   ✓ Agri-Pulse news articles")
    print("   ✓ Climate Suite with weather and pest alerts")
    print("   ✓ Planting season recommendations")
    print("\n💡 Next Steps:")
    print("   1. Create farmer and consumer accounts via registration")
    print("   2. Add products as a farmer")
    print("   3. Test the complete user journey")
    print("   4. Explore group buying features")
    print("\n🚀 Start the server: python manage.py runserver")
    print("   Visit: http://127.0.0.1:8000")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you've run migrations first:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")