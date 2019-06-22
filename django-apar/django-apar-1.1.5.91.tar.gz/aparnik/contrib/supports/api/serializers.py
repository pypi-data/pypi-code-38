from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.api.serializers import ModelSerializer

from ..models import *


class SupportDetailsSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    socials = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SupportDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Support
        fields = [
            'id',
            'url',
            'title',
            'online',
            'offline',
            'phone',
            'socials',
            'online_days',
        ]

    def get_image(self, obj):
        return self.get_image_ur(obj.image)

    def get_image_ur(self, filed):
        try:
            image = self.context['request'].build_absolute_uri(filed.url)
        except:
            image = None
        return image

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_socials(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.socials, many=True, read_only=True, context=self.context).data
