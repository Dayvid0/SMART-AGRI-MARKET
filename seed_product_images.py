"""
seed_product_images.py
Attaches generated images to the sample products in the database.
Run: python manage.py shell < seed_product_images.py
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from marketplace.models import Product

IMAGE_MAP = {
    'Fresh Tomatoes (Kampala Round)': 'products/tomatoes.png',
    'Sukuma Wiki (Kale)':             'products/kale.png',
    'White Maize (Dry Grain)':        'products/maize.png',
    'Dried Beans (Nambale)':          'products/beans.png',
    'Ripe Mangoes (Julie Variety)':   'products/mangoes.png',
    'Irish Potatoes (Victoria)':      'products/potatoes.png',
    'Passion Fruit (Purple)':         'products/passion_fruit.png',
    'Red Onions (Small Size)':        'products/onions.png',
    'Robusta Coffee (Parchment)':     'products/coffee.png',
    'Local Eggs (Free Range)':        'products/eggs.png',
}

updated = 0
for name, img_path in IMAGE_MAP.items():
    try:
        product = Product.objects.get(name=name)
        product.image = img_path
        product.save(update_fields=['image'])
        print(f"  ✓ {name}")
        updated += 1
    except Product.DoesNotExist:
        print(f"  ✗ Not found: {name}")
    except Exception as e:
        print(f"  ✗ Error for {name}: {e}")

print(f"\nDone. {updated} products updated with images.")
