"""Article serializer."""

from rest_framework import serializers
from .models import Article  # , Category


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer."""

    class Meta:
        """Article meta serializer."""

        model = Article
        fields = ('id', 'title', 'tldr', 'content',
                  'image', 'created_at', 'updated_at', 'slug_title')
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug_title')
        lookup_field = 'slug_title'
