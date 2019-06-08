from django.utils.text import Truncator
from django.urls import reverse
from rest_framework import serializers

from aparnik.settings import aparnik_settings
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer, ModelListPolymorphicSerializer
from ..models import News

UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


class NewsListSerializer(BaseModelListSerializer):

    user = serializers.SerializerMethodField()
    short_content = serializers.SerializerMethodField()
    cover_images = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(NewsListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = News
        fields = BaseModelListSerializer.Meta.fields + [
            'user',
            'title',
            'slug',
            'cover_images',
            'short_content',
            'is_published',
            'publish_date',
            'categories',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
            'user',
            'short_content',
            'cover_images',
            'categories',
        ]

    def get_user(self, obj):
        return UserSummeryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data

    def get_short_content(self, obj):
        return Truncator(obj.content).words(30)

    def get_cover_images(self, obj):
        return None if not obj.cover_images.all() else ModelListPolymorphicSerializer(obj.cover_images.all(), many=True, read_only=True, context=self.context).data

    def get_categories(self, obj):
        return None if not obj.categories.all() else ModelListPolymorphicSerializer(obj.categories.all(), many=True, read_only=True, context=self.context).data


# News Details Serializer
class NewsDetailSerializer(NewsListSerializer, BaseModelDetailSerializer):

    def __init__(self, *args, **kwargs):
        super(NewsDetailSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = News
        fields = NewsListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'content',
        ]

        read_only_fields = BaseModelDetailSerializer.Meta.read_only_fields + NewsListSerializer.Meta.read_only_fields + [
            'content']
