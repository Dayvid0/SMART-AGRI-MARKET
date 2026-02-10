from django.contrib import admin
from .models import NewsCategory, AgriNews

class AgriNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'news_type', 'is_featured', 'is_urgent', 'published_at', 'views']
    list_filter = ['news_type', 'is_featured', 'is_urgent']
    search_fields = ['title', 'content']

admin.site.register(NewsCategory)
admin.site.register(AgriNews, AgriNewsAdmin)