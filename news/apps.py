from django.apps import AppConfig

# Management commands that should NOT start the background scheduler
_SKIP_CMDS = frozenset({
    'migrate', 'makemigrations', 'check', 'shell', 'test',
    'collectstatic', 'createsuperuser', 'dbshell', 'showmigrations',
    'sqlmigrate', 'inspectdb', 'fetch_news', 'fetch_market_prices',
})


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import sys
        cmd = sys.argv[1] if len(sys.argv) > 1 else ''
        if cmd in _SKIP_CMDS:
            return
        # Guard against double-start from Django's dev-server reloader
        import os
        if os.environ.get('RUN_MAIN') == 'true' or 'runserver' not in sys.argv:
            try:
                from . import scheduler
                scheduler.start()
            except Exception:
                pass
