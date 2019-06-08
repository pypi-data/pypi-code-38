from rest_framework import serializers

from aparnik.api.serializers import ModelSerializer
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from ..models import FileField


class FileFieldSummarySerializer(BaseModelListSerializer):
    resourcetype = serializers.SerializerMethodField()

    class Meta:
        model = FileField
        fields = ['url'] + [
            'id',
            'type',
            'file_size',
            'file_size_readable',
            'resourcetype',
        ]

    def get_resourcetype(self, obj):
        return 'FileField'


class FileFieldListSerailizer(FileFieldSummarySerializer):

    file_url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(FileFieldListSerailizer, self).__init__(*args, **kwargs)

    class Meta:
        model = FileField
        fields = FileFieldSummarySerializer.Meta.fields + [
            'title',
            'file_url',
        ]

    def get_file_url(self, obj):
        return obj.url(request=self.context['request'])


class FileFieldDetailsSerailizer(BaseModelDetailSerializer, FileFieldListSerailizer):

    file_url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(FileFieldListSerailizer, self).__init__(*args, **kwargs)

    class Meta:
        model = FileField
        fields = FileFieldListSerailizer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
        ]

    def get_file_url(self, obj):
        return obj.url(request=self.context['request'])


class FileFieldCreateSerializer(ModelSerializer):

    file_url = serializers.SerializerMethodField()
    file_direct = serializers.FileField(required=False, write_only=True)
    file_s3 = serializers.URLField(required=False, write_only=True)
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(FileFieldCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = FileField
        fields = [
            'id',
            'file_direct',
            'file_s3',
            'file_url',
            'type',
            'size',
            'title',
            'resourcetype',
        ]

        read_only_fields = ['id', 'file_url', 'resourcetype']

    def get_file_url(self, obj):
        return obj.url(request=self.context['request'])

    def get_resourcetype(self, obj):
        return 'FileField'
