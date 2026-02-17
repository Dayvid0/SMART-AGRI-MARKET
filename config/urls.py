from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from marketplace.views import product_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),  
    path('', include('marketplace.urls')),
    path('reviews/', include('reviews.urls')),
    path('inputs/', include('inputs.urls')),
    path('news/', include('news.urls')),
    path('weather/', include('weather.urls')),  
    path('home/', product_list, name='home'),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)