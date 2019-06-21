from rest_framework import serializers

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from aparnik.contrib.categories.api.serializers import CategoryDetailsPolymorphicSerializer
from ..models import Book, Publisher, WriterTranslator

from aparnik.packages.shops.files.api.serializers import FileListSerializer, FileDetailSerializer


class BookListSerializer(FileListSerializer):

    class Meta:
        model = Book
        fields = FileListSerializer.Meta.fields + [
            'published_date',
        ]


class BookDetailsSerializer(BookListSerializer, FileDetailSerializer):
    categories = serializers.SerializerMethodField()
    publisher = serializers.SerializerMethodField()
    writers = serializers.SerializerMethodField()
    translators = serializers.SerializerMethodField()
    sample_book = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = BookListSerializer.Meta.fields + FileDetailSerializer.Meta.fields + [
            'sample_book',
            'publisher',
            'categories',
            'writers',
            'translators',
        ]

    def get_categories(self, obj):
        return CategoryDetailsPolymorphicSerializer(obj.category_obj, many=False, read_only=True, context=self.context).data

    def get_publisher(self, obj):
        return PublisherListSerializer(obj.publisher_obj, many=False, read_only=True, context=self.context).data

    def get_writers(self, obj):
        return WriterTranslatorListSerializer(obj.writers_obj, many=True, read_only=True, context=self.context).data

    def get_translators(self, obj):
        return WriterTranslatorListSerializer(obj.translators_obj, many=True, read_only=True, context=self.context).data

    def get_sample_book(self, obj):
        return FileFieldListSerailizer(obj.sample_book, many=False, read_only=True, context=self.context).data if obj.sample_book else None


class PublisherListSerializer(BaseModelListSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = BaseModelListSerializer.Meta.fields + [
            'url',
            'title',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())


class PublisherDetailsSerializer(BaseModelDetailSerializer, PublisherListSerializer):

    class Meta:
        model = Publisher
        fields = BaseModelDetailSerializer.Meta.fields + PublisherListSerializer.Meta.fields + [

        ]


class WriterTranslatorListSerializer(BaseModelListSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = WriterTranslator
        fields = BaseModelListSerializer.Meta.fields + [
            'url',
            'first_name',
            'last_name',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())


class WriterTranslatorDetailsSerializer(BaseModelDetailSerializer, WriterTranslatorListSerializer):

    class Meta:
        model = WriterTranslator
        fields = BaseModelDetailSerializer.Meta.fields + WriterTranslatorListSerializer.Meta.fields + [

        ]


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import BookSegment

    # Base Segment ListSegmentReview
    class SegmentBookListSerializer(BaseSegmentListSerializer):

        class Meta:
            model = BookSegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Book Segment Details
    class SegmentBookDetailSerializer(BaseSegmentDetailSerializer, SegmentBookListSerializer):

        class Meta:
            model = BookSegment
            fields = SegmentBookListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + SegmentBookListSerializer.Meta.read_only_fields + []