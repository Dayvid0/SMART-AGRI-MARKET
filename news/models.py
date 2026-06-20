from django.db import models
from accounts.models import User


class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='bi-newspaper')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "News Category"
        verbose_name_plural = "News Categories"


class AgriNews(models.Model):
    NEWS_TYPES = (
        ('government', 'Government Policy'),
        ('market', 'Market Update'),
        ('weather', 'Weather Alert'),
        ('technology', 'Agricultural Technology'),
        ('event', 'Event/Training'),
        ('advertisement', 'Advertisement'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )

    SOURCE_TYPES = (
        ('external_feed', 'External Feed'),
        ('user_submission', 'User Submission'),
    )

    title = models.CharField(max_length=300)
    news_type = models.CharField(max_length=20, choices=NEWS_TYPES)
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True)

    content = models.TextField()
    summary = models.TextField(help_text="Brief summary for preview")

    source = models.CharField(max_length=200, help_text="e.g., Ministry of Agriculture")
    source_url = models.URLField(blank=True)

    image = models.ImageField(upload_to='news/', blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False, help_text="Mark as urgent alert")

    # Workflow fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', db_index=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='external_feed')

    # User who submitted (farmers); published_by = admin who approved
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='submitted_news'
    )
    published_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='published_news'
    )

    published_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Agricultural News"
        verbose_name_plural = "Agricultural News"
        ordering = ['-published_at']
