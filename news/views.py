from django.shortcuts import render, get_object_or_404
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


@api_view(['POST'])
def toggle_like_news(request, news_id):
    news = TaggedNews.objects.get(id=news_id)

    if not news:
        return Response({"error": "News not found"}, status=404)

    news.likes += 1
    news.save()
    return Response({"success": True, "likes": news.likes})


@api_view(['GET'])
def fetch_news_by_slug(request, slug):
    news = get_object_or_404(TaggedNews, raw_news__slug=slug)
    serializer = TaggedNewsSerializer(news, many=False)
    return Response({"success": True, "news": serializer.data})
