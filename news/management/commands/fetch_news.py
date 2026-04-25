"""
Management command to fetch agricultural news from RSS feeds.

Sources:
  - FAO (UN Food & Agriculture Organization)
  - AllAfrica Agriculture
  - ReliefWeb Uganda Agriculture
  - IFAD East Africa
  - The East African (Agriculture section)

Usage:
  python manage.py fetch_news
  python manage.py fetch_news --max 20
  python manage.py fetch_news --source fao
"""

import feedparser
import requests
from datetime import datetime
from email.utils import parsedate_to_datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from news.models import AgriNews, NewsCategory


# ---------------------------------------------------------------------------
# RSS FEED CONFIGURATION
# ---------------------------------------------------------------------------
RSS_FEEDS = [
    {
        # Confirmed working: 20 entries — Uganda-specific humanitarian & food news
        'name': 'ReliefWeb Uganda',
        'url': 'https://reliefweb.int/updates/rss.xml?primary_country=254',
        'source': 'ReliefWeb Uganda',
        'news_type': 'government',
        'key': 'reliefweb_ug',
    },
    {
        # Confirmed working: 20 entries — Uganda country reports (food, agriculture, disasters)
        'name': 'ReliefWeb Uganda Reports',
        'url': 'https://reliefweb.int/updates/rss.xml?primary_country=254&type=report',
        'source': 'ReliefWeb Uganda',
        'news_type': 'government',
        'key': 'reliefweb_reports',
    },
    {
        # Confirmed working: 10 entries — Global agri-tech and farming news
        'name': 'AgWired',
        'url': 'https://feeds.feedburner.com/AgWired',
        'source': 'AgWired',
        'news_type': 'technology',
        'key': 'agwired',
    },
    {
        # Confirmed working: 12 entries — Crop protection, inputs, and pest management
        'name': 'CropLife International',
        'url': 'https://croplife.org/feed/',
        'source': 'CropLife International',
        'news_type': 'technology',
        'key': 'croplife',
    },
    {
        # East Africa agriculture & market news
        'name': 'ReliefWeb Food & Agriculture',
        'url': 'https://reliefweb.int/updates/rss.xml?primary_country=254&theme=4590',
        'source': 'ReliefWeb',
        'news_type': 'market',
        'key': 'reliefweb_food',
    },
]

# Keywords to filter for Uganda / East Africa relevance
RELEVANT_KEYWORDS = [
    'uganda', 'east africa', 'africa', 'agriculture', 'farming', 'crop',
    'farmer', 'food', 'harvest', 'climate', 'drought', 'maize', 'coffee',
    'fertilizer', 'seed', 'livestock', 'market', 'agri', 'rural',
    'kenya', 'tanzania', 'rwanda', 'sub-saharan',
]


def _parse_date(entry):
    """Extract a timezone-aware datetime from a feed entry."""
    # Try published_parsed (struct_time)
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return timezone.make_aware(dt)
        except Exception:
            pass
    # Try updated_parsed
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        try:
            dt = datetime(*entry.updated_parsed[:6])
            return timezone.make_aware(dt)
        except Exception:
            pass
    # Fallback to now
    return timezone.now()


def _is_relevant(entry, feed_config):
    """Check if an entry is relevant to agriculture/Uganda by keyword scan."""
    text = ' '.join([
        getattr(entry, 'title', ''),
        getattr(entry, 'summary', ''),
        getattr(entry, 'tags', [{}])[0].get('term', '') if hasattr(entry, 'tags') and entry.tags else '',
    ]).lower()

    # AllAfrica Uganda feed is always relevant
    if feed_config['key'] in ('allafrica', 'allafrica_ug'):
        return True

    return any(kw in text for kw in RELEVANT_KEYWORDS)


def _get_or_create_category(name, icon='bi-newspaper'):
    cat, _ = NewsCategory.objects.get_or_create(name=name, defaults={'icon': icon})
    return cat


CATEGORY_MAP = {
    'government': ('Government Policy', 'bi-building'),
    'market': ('Market Update', 'bi-graph-up'),
    'weather': ('Weather Alert', 'bi-cloud-lightning'),
    'technology': ('Agricultural Technology', 'bi-lightbulb'),
    'event': ('Events & Training', 'bi-calendar-event'),
    'advertisement': ('Advertisement', 'bi-megaphone'),
}


class Command(BaseCommand):
    help = 'Fetch agricultural news from RSS feeds (FAO, AllAfrica, ReliefWeb, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max',
            type=int,
            default=15,
            help='Maximum articles to fetch per feed (default: 15)',
        )
        parser.add_argument(
            '--source',
            type=str,
            default='all',
            help='Which feed to fetch: all, fao, allafrica, allafrica_ug, reliefweb, ifad, cgiar',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-import even if article already exists',
        )

    def handle(self, *args, **options):
        max_per_feed = options['max']
        source_filter = options['source'].lower()
        force = options['force']

        feeds = RSS_FEEDS
        if source_filter != 'all':
            feeds = [f for f in RSS_FEEDS if f['key'] == source_filter]
            if not feeds:
                self.stderr.write(self.style.ERROR(
                    f'Unknown source "{source_filter}". '
                    f'Valid options: all, {", ".join(f["key"] for f in RSS_FEEDS)}'
                ))
                return

        total_new = 0
        total_skipped = 0

        for feed_config in feeds:
            self.stdout.write(f'\n[RSS] Fetching: {feed_config["name"]} ...')

            try:
                # feedparser handles HTTP + SSL by itself
                parsed = feedparser.parse(
                    feed_config['url'],
                    request_headers={'User-Agent': 'AgriMarket News Bot/1.0'},
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   [WARN] Could not fetch feed: {e}'))
                continue

            if parsed.bozo and not parsed.entries:
                self.stdout.write(self.style.WARNING(
                    f'   [WARN] Feed error: {getattr(parsed, "bozo_exception", "unknown")}'))
                continue

            entries = parsed.entries[:max_per_feed]
            self.stdout.write(f'   Found {len(entries)} entries')

            # Get or create category
            cat_name, cat_icon = CATEGORY_MAP.get(
                feed_config['news_type'], ('General', 'bi-newspaper')
            )
            category = _get_or_create_category(cat_name, cat_icon)

            for entry in entries:
                title = getattr(entry, 'title', '').strip()
                if not title:
                    continue

                # Relevance filter (skip non-agri content from broad feeds)
                if not _is_relevant(entry, feed_config):
                    continue

                # Check duplicate by title (exact match)
                if not force and AgriNews.objects.filter(title=title).exists():
                    total_skipped += 1
                    continue

                # Build summary — use entry.summary or truncate content
                summary = getattr(entry, 'summary', '')
                if not summary and hasattr(entry, 'content'):
                    summary = entry.content[0].get('value', '')
                # Strip HTML tags simply
                import re
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                if len(summary) > 500:
                    summary = summary[:497] + '...'
                if not summary:
                    summary = title

                # Full content
                content = summary
                if hasattr(entry, 'content') and entry.content:
                    raw = entry.content[0].get('value', '')
                    content_clean = re.sub(r'<[^>]+>', '', raw).strip()
                    if content_clean:
                        content = content_clean

                # Source URL
                source_url = getattr(entry, 'link', '') or ''

                # Date
                pub_date = _parse_date(entry)

                try:
                    AgriNews.objects.create(
                        title=title,
                        news_type=feed_config['news_type'],
                        category=category,
                        content=content,
                        summary=summary,
                        source=feed_config['source'],
                        source_url=source_url,
                        published_at=pub_date,
                        is_featured=False,
                        is_urgent=False,
                        published_by=None,
                    )
                    total_new += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'   [OK] Saved: {title[:70]}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'   [WARN] Could not save "{title[:50]}": {e}')
                    )

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'Done! {total_new} new articles saved, {total_skipped} duplicates skipped.'
        ))
