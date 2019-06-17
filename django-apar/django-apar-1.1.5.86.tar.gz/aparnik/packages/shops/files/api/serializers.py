from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer, FileFieldSummarySerializer
from aparnik.packages.shops.products.api.serializers import ProductListSerializer, ProductDetailSerializer
from ..models import File


# Base File List
class FileListSerializer(ProductListSerializer):
    url = serializers.SerializerMethodField()
    file_download_request_url = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()
    file_property = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(FileListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = File
        fields = ProductListSerializer.Meta.fields + [
            'id',
            'url',
            'banner',
            'cover',
            'is_free',
            'file_download_request_url',
            'file_property',
        ]

        read_only_fields = ProductListSerializer.Meta.read_only_fields + ['url', 'file_download_request_url',
                                                                          'banner', 'cover', 'file_property',
                                                                          ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_file_download_request_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_file_download_request_uri())

    def get_banner(self, obj):
        return FileFieldListSerailizer(obj.banner, many=False, read_only=True, context=self.context).data if obj.banner else None

    def get_cover(self, obj):
        return FileFieldListSerailizer(obj.cover, many=False, read_only=True,
                                       context=self.context).data if obj.cover else None

    def get_file_property(self, obj):
        return FileFieldSummarySerializer(obj.file_obj, many=False, read_only=True,
                                       context=self.context).data if obj.file_obj else None


# Base File Details
class FileDetailSerializer(FileListSerializer, ProductDetailSerializer):

    def __init__(self, *args, **kwargs):
        super(FileDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = File
        fields = FileListSerializer.Meta.fields + ProductDetailSerializer.Meta.fields + [
            'description',

        ]
        read_only_fields = FileListSerializer.Meta.read_only_fields + ProductDetailSerializer.Meta.read_only_fields + [
            'description']


# Base File List Polymorphic
class FileListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):

        model_serializer_mapping = {
            File: FileListSerializer,
        }

        # Book
        if is_app_installed('aparnik.packages.educations.books'):
            from aparnik.packages.educations.books.models import Book
            from aparnik.packages.educations.books.api.serializers import BookListSerializer
            model_serializer_mapping[Book] = BookListSerializer

        # Course File
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.packages.educations.courses.models import CourseFile
            from aparnik.packages.educations.courses.api.serializers import CourseFileListSerializer
            model_serializer_mapping[CourseFile] = CourseFileListSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(FileListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Base Model Details Polymorphic
class FileDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):

        model_serializer_mapping = {
            File: FileListSerializer,
        }

        # Book
        if is_app_installed('aparnik.packages.educations.books'):
            from aparnik.packages.educations.books.models import Book
            from aparnik.packages.educations.books.api.serializers import BookDetailsSerializer
            model_serializer_mapping[Book] = BookDetailsSerializer

        # Course File
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.packages.educations.courses.models import CourseFile
            from aparnik.packages.educations.courses.api.serializers import CourseFileDetailSerializer
            model_serializer_mapping[CourseFile] = CourseFileDetailSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(FileDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
