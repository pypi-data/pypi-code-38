from rest_framework import serializers

from .models import Category, FAQ


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = ['order', 'question', 'answer']


class CategorySerializer(serializers.ModelSerializer):
    faqs = FAQSerializer(many=True)

    class Meta:
        model = Category
        fields = ['order', 'name', 'faqs']
