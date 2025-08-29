from rest_framework import serializers
from news.models import *
from category.serializers import CategorySerializer, TagSerializer


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Source


class NewsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = NewsType


class RawNewsSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)

    class Meta:
        fields = "__all__"
        model = RawNews


class TaggedNewsSerializer(serializers.ModelSerializer):
    raw_news = RawNewsSerializer(read_only=True)
    news_type = NewsTypeSerializer(read_only=True)

    tags = TagSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        fields = "__all__"
        model = TaggedNews
