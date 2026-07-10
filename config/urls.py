from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve as static_serve
from django.http import FileResponse
from marketplace.views import product_list
import os


def service_worker_view(request):
    """Serve sw.js with correct headers for PWA registration."""
    sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'sw.js')
    response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


urlpatterns = [
    # ── PWA routes (must be at root scope) ──
    path('sw.js', service_worker_view, name='service-worker'),
    path('manifest.json', static_serve,
         {'document_root': settings.STATICFILES_DIRS[0], 'path': 'manifest.json'},
         name='manifest'),
    path('offline/', TemplateView.as_view(template_name='offline.html'),
         name='offline'),

    # ── App routes ──
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),  
    path('', include('marketplace.urls')),

    path('inputs/', include('inputs.urls')),
    path('news/', include('news.urls')),
    path('weather/', include('weather.urls')),  
    path('home/', product_list, name='home'),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)