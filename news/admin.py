from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from .models import NewsCategory, AgriNews


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']


@admin.register(AgriNews)
class AgriNewsAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'source_type', 'news_type',
        'submitted_by', 'is_featured', 'is_urgent', 'published_at', 'views',
    ]
    list_filter = ['status', 'source_type', 'news_type', 'is_featured', 'is_urgent']
    search_fields = ['title', 'content', 'source']
    readonly_fields = ['views', 'published_at', 'submitted_by']
    actions = ['approve_articles', 'reject_articles', 'mark_featured', 'mark_urgent']

    fieldsets = (
        (None, {
            'fields': ('title', 'news_type', 'category', 'status', 'source_type'),
        }),
        ('Content', {
            'fields': ('summary', 'content', 'image'),
        }),
        ('Source', {
            'fields': ('source', 'source_url'),
        }),
        ('Flags', {
            'fields': ('is_featured', 'is_urgent'),
        }),
        ('Authorship', {
            'fields': ('submitted_by', 'published_by', 'published_at', 'views'),
        }),
    )

    def approve_articles(self, request, queryset):
        pending = queryset.filter(status='pending')
        count = pending.update(status='published', published_by=request.user)
        self.message_user(request, f'{count} article(s) approved and published.', messages.SUCCESS)
    approve_articles.short_description = 'Approve selected articles'

    def reject_articles(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} article(s) rejected.', messages.WARNING)
    reject_articles.short_description = 'Reject selected articles'

    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} article(s) marked as featured.', messages.SUCCESS)
    mark_featured.short_description = 'Mark as featured'

    def mark_urgent(self, request, queryset):
        count = queryset.update(is_urgent=True)
        self.message_user(request, f'{count} article(s) marked as urgent.', messages.SUCCESS)
    mark_urgent.short_description = 'Mark as urgent alert'
