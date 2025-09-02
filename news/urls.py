from django.urls import path
from news.views import get_news, toggle_like_news, fetch_news_by_slug, fetch_news_meta_by_slug, tagged_news_detail

urlpatterns = [
    path('', view=get_news, name='get_news'),
    path('<slug:slug>', view=fetch_news_by_slug, name='fetch_news_by_slug'),
    path("meta/<slug:slug>/", fetch_news_meta_by_slug,
         name="fetch-news-meta-by-slug"),
    path("<slug:slug>/", fetch_news_by_slug, name="fetch-news-by-slug"),
    path("api/meta/<slug:slug>/", fetch_news_meta_by_slug,
         name="fetch-news-meta-by-slug"),
    path("api/<slug:slug>/", tagged_news_detail, name="tagged-news-detail"),
    path('like/<int:news_id>/',
         view=toggle_like_news, name="toggle_like_news"),
]
