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


class TaggedNewsMetaSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="raw_news.title", read_only=True)
    description = serializers.SerializerMethodField()
    image = serializers.CharField(source="raw_news.img_url", read_only=True)
    url = serializers.SerializerMethodField()

    tags = TagSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = TaggedNews
        fields = ["title", "description", "image",
                  "url", "likes", "tags", "categories"]

    def get_description(self, obj):
        return obj.summary or obj.raw_news.description

    def get_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/news/{obj.raw_news.slug}/")
        return f"/news/{obj.raw_news.slug}/"
