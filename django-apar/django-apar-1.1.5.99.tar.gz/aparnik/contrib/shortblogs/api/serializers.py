from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer

from ..models import ShortBlog


class ShortBlogListSerializer(ModelSerializer):
    datetime = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ShortBlogListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ShortBlog
        fields = [
            'id',
            'title',
            'content',
            'datetime',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_datetime(self, obj):
        return obj.update_at

    # def get_category(self, obj):
    #     return CategoryListSerializer(obj.category, many=True, read_only=True, context=self.context).data


class ShortBlogDetailSerializer(ShortBlogListSerializer):

    def __init__(self, *args, **kwargs):
        super(ShortBlogDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ShortBlog
        fields = ShortBlogListSerializer.Meta.fields + [
        ]

