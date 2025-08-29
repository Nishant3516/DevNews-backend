from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Category
from .serializers import CategorySerializer
from rest_framework.response import Response
# Create your views here.


@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)
