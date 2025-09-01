from django.urls import path
from news.views import get_news, toggle_like_news

urlpatterns = [
    path('', view=get_news, name='get_news'),
    path('/like/<int:news_id>/',
         view=toggle_like_news, name="toggle_like_news"),
]
