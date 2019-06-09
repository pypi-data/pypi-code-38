from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer

from aparnik.contrib.shortblogs.api.serializers import ShortBlogDetailSerializer
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from aparnik.contrib.segments.api.serializers import BaseSegmentListPolymorphicSerializer
from ..models import Information


class AboutusDestailSerializer(ModelSerializer):

    socials = serializers.SerializerMethodField()
    short_blogs = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    slider_segment = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(AboutusDestailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Information
        fields = [
            'id',
            'website',
            'address',
            'phone',
            'email',
            'about_us',
            'image',
            'socials',
            'short_blogs',
            'slider_segment',
        ]

    def get_socials(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.socials, many=True, read_only=True, context=self.context).data

    def get_short_blogs(self, obj):
        return ShortBlogDetailSerializer(obj.short_blogs, many=True, read_only=True, context=self.context).data

    def get_image(self, obj):
        return FileFieldListSerailizer(obj.image, many=False, read_only=True, context=self.context).data

    def get_slider_segment(self, obj):
        return BaseSegmentListPolymorphicSerializer(obj.slider_segment_obj, many=False, read_only=True, context=self.context).data if obj.slider_segment_obj else None

