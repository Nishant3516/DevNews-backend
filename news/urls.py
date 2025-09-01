from django.urls import path
from news.views import get_news, toggle_like_news, fetch_news_by_slug

urlpatterns = [
    path('', view=get_news, name='get_news'),
    path('<slug:slug>', view=fetch_news_by_slug, name='fetch_news_by_slug'),
    path('like/<int:news_id>/',
         view=toggle_like_news, name="toggle_like_news"),
]
