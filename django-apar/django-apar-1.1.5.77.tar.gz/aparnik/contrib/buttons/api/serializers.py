from rest_framework import serializers

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer, \
    ModelListPolymorphicSerializer
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from ..models import Button


class ButtonListSerializer(BaseModelListSerializer):
    icon = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()

    class Meta:
        model = Button
        fields = BaseModelListSerializer.Meta.fields + [
            'title',
            'icon',
            'background_color',
            'icon_color',
            'title_color',
            'model',
        ]
        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + ['title',
                                                                            'icon',
                                                                            'background_color',
                                                                            'icon_color',
                                                                            'title_color',
                                                                            'model',
                                                                            ]

    def get_icon(self, obj):
        return FileFieldListSerailizer(obj.icon, many=False, read_only=True, context=self.context).data if obj.icon \
            else None

    def get_model(self, obj):
        return ModelListPolymorphicSerializer(obj.model_obj.get_real_instance(), many=False, read_only=True, context=self.context).data


class ButtonDetailsSerializer(ButtonListSerializer, BaseModelDetailSerializer):
    class Meta:
        model = Button
        fields = ButtonListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [

        ]


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import ButtonSegment

    # Base Segment ListSegmentReview
    class SegmentButtonListSerializer(BaseSegmentListSerializer):

        class Meta:
            model = ButtonSegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Book Segment Details
    class SegmentButtonDetailSerializer(BaseSegmentDetailSerializer, SegmentButtonListSerializer):

        class Meta:
            model = ButtonSegment
            fields = SegmentButtonListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + []
