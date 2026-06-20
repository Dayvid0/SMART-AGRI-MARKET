from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('submit/', views.submit_news, name='submit_news'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
]
