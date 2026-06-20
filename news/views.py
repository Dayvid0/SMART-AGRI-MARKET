from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import AgriNews, NewsCategory


def news_list(request):
    news_items = AgriNews.objects.filter(status='published').order_by('-published_at')

    news_type = request.GET.get('type')
    search_query = request.GET.get('search')
    category_id = request.GET.get('category')

    if news_type:
        news_items = news_items.filter(news_type=news_type)
    if category_id:
        news_items = news_items.filter(category_id=category_id)
    if search_query:
        news_items = news_items.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(source__icontains=search_query)
        )

    featured_news = AgriNews.objects.filter(status='published', is_featured=True).order_by('-published_at')[:3]
    urgent_alerts = AgriNews.objects.filter(status='published', is_urgent=True).order_by('-published_at')[:5]
    categories = NewsCategory.objects.all()

    context = {
        'news_items': news_items[:30],
        'featured_news': featured_news,
        'urgent_alerts': urgent_alerts,
        'categories': categories,
        'selected_type': news_type,
        'selected_category': category_id,
        'search_query': search_query,
        'total_count': news_items.count(),
    }
    return render(request, 'news/news_list.html', context)


def news_detail(request, pk):
    news = get_object_or_404(AgriNews, pk=pk, status='published')
    news.views += 1
    news.save(update_fields=['views'])

    related_news = AgriNews.objects.filter(
        news_type=news.news_type, status='published'
    ).exclude(pk=pk)[:4]

    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'news/news_detail.html', context)


@login_required
def submit_news(request):
    categories = NewsCategory.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        news_type = request.POST.get('news_type', '')
        content = request.POST.get('content', '').strip()
        summary = request.POST.get('summary', '').strip()
        source = request.POST.get('source', '').strip()
        source_url = request.POST.get('source_url', '').strip()
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        errors = []
        if not title:
            errors.append('Title is required.')
        if not news_type:
            errors.append('Please select a news type.')
        if not content:
            errors.append('Content is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            if not summary:
                summary = content[:300] + '...' if len(content) > 300 else content
            if not source:
                source = request.user.get_full_name() or request.user.username

            category = None
            if category_id:
                category = NewsCategory.objects.filter(pk=category_id).first()

            AgriNews.objects.create(
                title=title,
                news_type=news_type,
                category=category,
                content=content,
                summary=summary,
                source=source,
                source_url=source_url,
                image=image,
                status='pending',
                source_type='user_submission',
                submitted_by=request.user,
            )
            messages.success(
                request,
                'Your article has been submitted and is awaiting admin approval. Thank you!'
            )
            return redirect('news:news_list')

    context = {
        'categories': categories,
        'news_types': AgriNews.NEWS_TYPES,
    }
    return render(request, 'news/submit_news.html', context)
