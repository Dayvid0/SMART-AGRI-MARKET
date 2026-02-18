"""
Django management command to fetch market prices from external APIs

Usage:
    python manage.py fetch_market_prices
    python manage.py fetch_market_prices --days 7
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from marketplace.models import ExternalMarketPrice
from marketplace.services.price_fetcher import WFPPriceFetcher
from datetime import timedelta


class Command(BaseCommand):
    help = 'Fetch latest market prices from WFP API and store in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to look back for price data (default: 30)'
        )
        parser.add_argument(
            '--clear-old',
            action='store_true',
            help='Mark prices older than 60 days as inactive'
        )

    def handle(self, *args, **options):
        days_back = options['days']
        clear_old = options['clear_old']
        
        self.stdout.write(self.style.NOTICE(f'Fetching market prices from WFP API (last {days_back} days)...'))
        
        # Initialize fetcher
        fetcher = WFPPriceFetcher()
        
        # Fetch prices
        try:
            prices = fetcher.fetch_latest_prices(days_back=days_back)
            
            if not prices:
                self.stdout.write(self.style.WARNING('No prices fetched from API'))
                return
            
            # Store prices in database
            created_count = 0
            updated_count = 0
            
            for price_data in prices:
                # Check if price already exists
                existing = ExternalMarketPrice.objects.filter(
                    product_name=price_data['product_name'],
                    date_recorded=price_data['date_recorded'],
                    source='wfp'
                ).first()
                
                if existing:
                    # Update existing price
                    existing.price = price_data['price']
                    existing.unit = price_data['unit']
                    existing.market_location = price_data['market_location']
                    existing.is_active = True
                    existing.save()
                    updated_count += 1
                else:
                    # Create new price record
                    ExternalMarketPrice.objects.create(
                        product_name=price_data['product_name'],
                        price=price_data['price'],
                        unit=price_data['unit'],
                        market_location=price_data['market_location'],
                        source='wfp',
                        date_recorded=price_data['date_recorded'],
                        currency=price_data.get('currency', 'UGX'),
                        is_active=True
                    )
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully processed {len(prices)} prices: '
                    f'{created_count} created, {updated_count} updated'
                )
            )
            
            # Clear old prices if requested
            if clear_old:
                cutoff_date = timezone.now().date() - timedelta(days=60)
                old_count = ExternalMarketPrice.objects.filter(
                    date_recorded__lt=cutoff_date,
                    is_active=True
                ).update(is_active=False)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Marked {old_count} old prices as inactive')
                )
            
            # Show summary of current prices
            active_prices = ExternalMarketPrice.objects.filter(is_active=True).count()
            self.stdout.write(
                self.style.NOTICE(f'Total active external prices in database: {active_prices}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error fetching prices: {str(e)}')
            )
            raise
