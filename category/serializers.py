from .models import Category, Tag
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Category


class TagSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = "__all__"
        model = Tag
