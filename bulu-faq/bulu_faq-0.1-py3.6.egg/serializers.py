from rest_framework import serializers

from .models import Category, FAQ


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = ['id', 'order', 'question', 'answer', 'category']


class CategorySerializer(serializers.ModelSerializer):
    faqs = FAQSerializer(many=True)

    class Meta:
        model = Category
        fields = '__all__'
