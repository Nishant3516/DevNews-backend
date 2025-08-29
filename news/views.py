from django.shortcuts import render
from news.models import TaggedNews
from rest_framework.decorators import api_view
from rest_framework.response import Response
from news.serializers import TaggedNewsSerializer

# Create your views here.


@api_view(['GET'])
def get_news(request):
    news = (
        TaggedNews.objects
        .select_related("raw_news", "news_type")
        .prefetch_related("categories", "tags")
        .order_by("-raw_news__published_at")
    )

    category_ids = request.GET.getlist('category')
    if category_ids:
        category_ids = [int(c) for c in category_ids]
        news = news.filter(categories__id__in=category_ids).distinct()

    serializer = TaggedNewsSerializer(news, many=True)
    return Response(serializer.data)


# instance 1 - normal User
# models
# fetch_news
# process_news - filter query

# instance 2- cron jobs 1
# news=fetch_news
# process_news(news) - summary()
# process_blog(blog) - summary()


# cron job 2
# news=blog
# process_blog(news) - summary()
