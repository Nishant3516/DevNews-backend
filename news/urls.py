from django.urls import path
from news.views import get_news

urlpatterns = [
    path('', view=get_news, name='get_news')
]
