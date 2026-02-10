from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import AgriNews, NewsCategory

def news_list(request):
    """
    Agri-Pulse news listing
    """
    news_items = AgriNews.objects.all()
    
    # Filters
    news_type = request.GET.get('type')
    search_query = request.GET.get('search')
    
    if news_type:
        news_items = news_items.filter(news_type=news_type)
    
    if search_query:
        news_items = news_items.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Featured and urgent news
    featured_news = news_items.filter(is_featured=True)[:3]
    urgent_alerts = news_items.filter(is_urgent=True)[:5]
    
    categories = NewsCategory.objects.all()
    
    context = {
        'news_items': news_items[:20],
        'featured_news': featured_news,
        'urgent_alerts': urgent_alerts,
        'categories': categories,
        'selected_type': news_type,
        'search_query': search_query,
    }
    
    return render(request, 'news/news_list.html', context)


def news_detail(request, pk):
    """
    Single news article
    """
    news = get_object_or_404(AgriNews, pk=pk)
    
    # Increment views
    news.views += 1
    news.save()
    
    # Related news
    related_news = AgriNews.objects.filter(
        news_type=news.news_type
    ).exclude(pk=pk)[:4]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    
    return render(request, 'news/news_detail.html', context)