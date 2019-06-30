from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer

from ..models import Bookmark
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from aparnik.settings import aparnik_settings

UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


# Bookmark List Serializer
class BookmarkListSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BookmarkListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Bookmark
        fields = [
            'url',
            'model'
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_model(self, obj):
        return ModelListPolymorphicSerializer(obj.model_obj, many=False, read_only=True, context=self.context).data


# Bookmark Details Serializer
class BookmarkDetailSerializer(BookmarkListSerializer):
    user = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BookmarkDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Bookmark
        fields = BookmarkListSerializer.Meta.fields + [
            'user'
        ]

    def get_user(self, obj):
        return UserSummeryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data