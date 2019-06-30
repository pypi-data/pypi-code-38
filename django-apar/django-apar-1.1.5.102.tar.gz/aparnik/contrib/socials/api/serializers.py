from rest_framework import serializers

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer
from ..models import SocialNetwork
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer


class SocialNetworkDestailSerializer(BaseModelDetailSerializer):

    icon = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SocialNetworkDestailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = SocialNetwork
        fields = BaseModelDetailSerializer.Meta.fields + [
            'link',
            'icon',
            'title',
            'android_app_shortcut',
            'ios_app_shortcut',
            'value',
        ]

    def get_icon(self, obj):
        return FileFieldListSerailizer(obj.icon, many=False, read_only=True, context=self.context).data


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import SocialNetworkSegment

    # Base Segment ListSegmentReview
    class SegmentSocialNetworkListSerializer(BaseSegmentListSerializer):

        class Meta:
            model = SocialNetworkSegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Book Segment Details
    class SegmentSocialNetworkDetailSerializer(BaseSegmentDetailSerializer, SegmentSocialNetworkListSerializer):

        class Meta:
            model = SocialNetworkSegment
            fields = SegmentSocialNetworkListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + SegmentSocialNetworkListSerializer.Meta.read_only_fields + []

