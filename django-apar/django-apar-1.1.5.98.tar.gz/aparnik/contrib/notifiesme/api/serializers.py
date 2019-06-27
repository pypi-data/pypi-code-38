from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer, ModelListPolymorphicSerializer
from aparnik.settings import aparnik_settings
from ..models import NotifyMe


UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


class NotifyMeListSerializer(BaseModelListSerializer):
    user = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(NotifyMeListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = NotifyMe
        fields = BaseModelListSerializer.Meta.fields + [
            'user',
            'model',
            'update_at',
        ]

    def get_user(self, obj):
        return UserSummeryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data

    def get_model(self, obj):
        return ModelListPolymorphicSerializer(obj.model_obj, many=False, read_only=True, context=self.context).data
