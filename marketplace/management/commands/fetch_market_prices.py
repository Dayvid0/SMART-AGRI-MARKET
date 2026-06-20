"""
Management command to fetch Uganda food prices from HDX (WFP VAM dataset).

Usage:
    python manage.py fetch_market_prices
    python manage.py fetch_market_prices --days 90
    python manage.py fetch_market_prices --clear-old
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from marketplace.models import ExternalMarketPrice
from marketplace.services.price_fetcher import fetch_hdx_prices


class Command(BaseCommand):
    help = 'Fetch Uganda food prices from HDX/WFP and store in ExternalMarketPrice'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=60,
            help='How many days of price history to fetch (default: 60)',
        )
        parser.add_argument(
            '--clear-old', action='store_true',
            help='Mark prices older than 90 days as inactive',
        )

    def handle(self, *args, **options):
        days_back = options['days']
        self.stdout.write(f'[prices] Fetching HDX/WFP Uganda prices (last {days_back} days)…')

        prices = fetch_hdx_prices(days_back=days_back)

        if not prices:
            self.stdout.write(self.style.WARNING('[prices] No prices returned — check network or HDX availability.'))
            return

        created = updated = skipped = 0

        for p in prices:
            obj, was_created = ExternalMarketPrice.objects.update_or_create(
                product_name=p['product_name'],
                date_recorded=p['date_recorded'],
                market_location=p['market_location'],
                source='wfp',
                defaults={
                    'price': p['price'],
                    'unit': p['unit'],
                    'currency': p['currency'],
                    'is_active': True,
                    'raw_data': None,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'[prices] Done — {created} created, {updated} updated, {skipped} skipped.'
        ))

        if options['clear_old']:
            cutoff = timezone.now().date() - timedelta(days=90)
            old = ExternalMarketPrice.objects.filter(
                date_recorded__lt=cutoff, is_active=True
            ).update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f'[prices] Marked {old} old records inactive.'))

        total_active = ExternalMarketPrice.objects.filter(is_active=True).count()
        self.stdout.write(f'[prices] Total active price records: {total_active}')
