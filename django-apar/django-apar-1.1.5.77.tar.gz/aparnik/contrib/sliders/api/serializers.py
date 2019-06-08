from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.utils.utils import is_app_installed
from aparnik.api.serializers import ModelSerializer
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from ..models import *


# Slider Details Slider
class SliderDetailsSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SliderDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Slider
        fields = [
            'id',
            'url',
            'image',
            'name',
        ]

    def get_image(self, obj):
        return FileFieldListSerailizer(obj.image, many=False, read_only=True, context=self.context).data

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())


# SliderVideo
class SliderVideoDetailsSerializer(SliderDetailsSerializer):

    video = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SliderVideoDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = SliderVideo
        fields = SliderDetailsSerializer.Meta.fields + [
            'video',
        ]

    def get_video(self, obj):
        return FileFieldListSerailizer(obj.video, many=False, read_only=True, context=self.context).data


class SliderSocialNetworkDetailsSerializer(SliderDetailsSerializer):

    social = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SliderSocialNetworkDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = SliderSocialNetwork
        fields = SliderDetailsSerializer.Meta.fields + [
            'social',
        ]

    def get_social(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.social, many=False, read_only=True, context=self.context).data


# SliderLink
class SliderLinkNetworkDetailsSerializer(SliderDetailsSerializer):

    def __init__(self, *args, **kwargs):
        super(SliderLinkNetworkDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = SliderLink
        fields = SliderDetailsSerializer.Meta.fields + [
            'link',
        ]


# SliderBaseModel
class SliderBaseModelDetailsSerializer(SliderDetailsSerializer):
    model = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SliderBaseModelDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = SliderBaseModel
        fields = SliderDetailsSerializer.Meta.fields + [
            'model',
        ]

    def get_model(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.model, many=False, read_only=True, context=self.context).data


class SliderDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):

        self.model_serializer_mapping = {
            Slider: SliderDetailsSerializer,
            SliderVideo: SliderVideoDetailsSerializer,
            SliderSocialNetwork: SliderSocialNetworkDetailsSerializer,
            SliderLink: SliderLinkNetworkDetailsSerializer,
            SliderBaseModel: SliderBaseModelDetailsSerializer
        }
        super(SliderDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import SliderSegment

    # Base Segment ListSegmentReview
    class SegmentSliderListSerializer(BaseSegmentListSerializer):

        class Meta:
            model = SliderSegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Segmt Details
    class SegmentSliderDetailSerializer(BaseSegmentDetailSerializer, SegmentSliderListSerializer):

        class Meta:
            model = SliderSegment
            fields = SegmentSliderListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + SegmentSliderListSerializer.Meta.read_only_fields + []
