from rest_framework import serializers
from ..models import CategoryModel


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ['serial', 'title', 'slug', 'description', 'status']