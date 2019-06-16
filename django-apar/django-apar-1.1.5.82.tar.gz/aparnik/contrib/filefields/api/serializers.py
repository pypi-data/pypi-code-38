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

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + ['url', 'type', 'file_size', 'file_size_readable', 'resourcetype']

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
            'is_encrypt_needed',
            'is_lock',
            'seconds',
        ]

        read_only_fields = FileFieldSummarySerializer.Meta.read_only_fields + ['file_url', 'is_lock', 'seconds']

    def get_file_url(self, obj):
        return obj.url(request=self.context['request'])


class FileFieldDetailsSerailizer(BaseModelDetailSerializer, FileFieldListSerailizer):

    file_direct = serializers.FileField(required=False, write_only=True)
    file_s3 = serializers.URLField(required=False, write_only=True)

    def __init__(self, *args, **kwargs):
        super(FileFieldListSerailizer, self).__init__(*args, **kwargs)

    class Meta:
        model = FileField
        fields = FileFieldListSerailizer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'file_direct',
            'file_s3',
        ]

        read_only_fields = FileFieldListSerailizer.Meta.read_only_fields + BaseModelDetailSerializer.Meta.read_only_fields
