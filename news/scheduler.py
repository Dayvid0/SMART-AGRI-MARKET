import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)


def fetch_news_job():
    from django.core.management import call_command
    call_command('fetch_news', max=15, source='all')


def fetch_prices_job():
    from django.core.management import call_command
    call_command('fetch_market_prices', days=60)


def start():
    scheduler = BackgroundScheduler(timezone='UTC')
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(
        fetch_news_job,
        trigger=IntervalTrigger(hours=6),
        id='fetch_agricultural_news',
        name='Fetch Agricultural News from RSS Feeds',
        replace_existing=True,
        misfire_grace_time=600,
    )

    scheduler.add_job(
        fetch_prices_job,
        trigger=IntervalTrigger(hours=12),
        id='fetch_market_prices',
        name='Fetch Uganda Food Prices from HDX/WFP',
        replace_existing=True,
        misfire_grace_time=600,
    )

    try:
        scheduler.start()
        logger.info('Scheduler started — news every 6h, prices every 12h.')
    except Exception as exc:
        logger.warning('Scheduler could not start: %s', exc)
