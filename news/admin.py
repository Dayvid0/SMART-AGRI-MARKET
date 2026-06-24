from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils import timezone
from .models import NewsCategory, AgriNews


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']


@admin.register(AgriNews)
class AgriNewsAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status_badge', 'source_type', 'news_type',
        'submitted_by', 'is_featured', 'is_urgent', 'published_at', 'views',
    ]
    list_filter = ['status', 'source_type', 'news_type', 'is_featured', 'is_urgent']
    search_fields = ['title', 'content', 'source']
    readonly_fields = ['views', 'published_at', 'submitted_by']
    list_editable = []          # keep empty; status is changed via actions or inline edit
    ordering = ['status', '-published_at']   # pending articles float to the top
    actions = ['approve_articles', 'reject_articles', 'mark_featured', 'mark_urgent']
    list_per_page = 30

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

    # ── Coloured status badge ────────────────────────────────
    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        colours = {
            'pending':   ('#fef3c7', '#92400e', '⏳ Pending'),
            'published': ('#d1fae5', '#065f46', '✅ Published'),
            'rejected':  ('#fee2e2', '#991b1b', '❌ Rejected'),
        }
        bg, fg, label = colours.get(obj.status, ('#f3f4f6', '#374151', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:0.8rem;font-weight:600;">{}</span>',
            bg, fg, label
        )

    # ── Actions ──────────────────────────────────────────────
    def approve_articles(self, request, queryset):
        pending = queryset.filter(status='pending')
        count = pending.update(status='published', published_by=request.user)
        self.message_user(
            request,
            f'✅ {count} article(s) approved and now live on the site.',
            messages.SUCCESS
        )
    approve_articles.short_description = '✅ Approve selected articles (publish to site)'

    def reject_articles(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(
            request,
            f'❌ {count} article(s) rejected.',
            messages.WARNING
        )
    reject_articles.short_description = '❌ Reject selected articles'

    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'⭐ {count} article(s) marked as featured.', messages.SUCCESS)
    mark_featured.short_description = '⭐ Mark as featured'

    def mark_urgent(self, request, queryset):
        count = queryset.update(is_urgent=True)
        self.message_user(request, f'🚨 {count} article(s) marked as urgent.', messages.SUCCESS)
    mark_urgent.short_description = '🚨 Mark as urgent alert'
