from rest_framework import serializers

from aparnik.settings import aparnik_settings
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer, ModelListPolymorphicSerializer
from ..models import NotificationForSingleUser

UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


class NotificationListSerializer(BaseModelListSerializer):

    url_read = serializers.SerializerMethodField()
    notification_type = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    from_user = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(NotificationListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
            # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = NotificationForSingleUser
        fields = BaseModelListSerializer.Meta.fields + [
            'url_read',
            'title',
            'description',
            'notification_type',
            'datetime',
            'is_read',
            'model',
            'from_user',
        ]

    def get_notification_type(self, obj):
        return obj.get_notification_type_json_display()

    def get_is_read(self, obj):
        return obj.get_user_is_read(user=self.context['request'].user)

    def get_url_read(self, obj):

        return self.context['request'].build_absolute_uri(obj.get_api_read_uri())

    def get_model(self, obj):
        return ModelListPolymorphicSerializer(obj.model_obj, many=False, read_only=True, context=self.context).data if obj.model_obj else None

    def get_from_user(self, obj):
        return UserSummeryListSerializer(obj.from_user_obj, many=False, read_only=True, context=self.context).data if obj.from_user_obj else None


class NotificationDetailSerializer(BaseModelDetailSerializer, NotificationListSerializer):

    class Meta:
        model = NotificationForSingleUser
        fields = BaseModelDetailSerializer.Meta.fields + NotificationListSerializer.Meta.fields + [

        ]
