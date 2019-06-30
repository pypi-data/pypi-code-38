# -*- coding: utf-8 -*-


from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from ..models import Category


# Category List Serializer
class CategoryListSerializer(BaseModelListSerializer):
    url_model = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    child_count = serializers.SerializerMethodField()
    url_childs = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = BaseModelDetailSerializer.Meta.fields + [
            'title',
            'image',
            'url_model',
            'child_count',
            'url_childs'
        ]

    def get_url_model(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_model_list_uri())

    def get_image(self, obj):
        from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
        return FileFieldListSerailizer(obj.image, many=False, read_only=True, context=self.context).data

    def get_child_count(self, obj):
        return Category.objects.childs_count(category_obj=obj)

    def get_url_childs(self, obj):
        if Category.objects.childs_count(obj) > 0:
            return self.context['request'].build_absolute_uri(obj.get_api_child_uri())
        return None


# Category Details Serializer
class CategoryDetailsSerializer(CategoryListSerializer, BaseModelDetailSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = CategoryListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'description',
            'parent',
        ]

    def get_parent(self, obj):
        return CategoryListPolymorphicSerializer(obj.parent_obj, many=False, read_only=True,
                                                 context=self.context).data if obj.parent_obj is not None else None


# Category List Polymorphic
class CategoryListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            Category: CategoryDetailsSerializer,
        }
        super(CategoryListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Category Details Polymorphic
class CategoryDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            Category: CategoryDetailsSerializer,
        }
        super(CategoryDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import CategorySegment

    # Base Segment ListSegmentReview
    class SegmentCategoryListSerializer(BaseSegmentListSerializer):
        class Meta:
            model = CategorySegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Book Segment Details
    class SegmentCategoryDetailSerializer(BaseSegmentDetailSerializer, SegmentCategoryListSerializer):
        class Meta:
            model = CategorySegment
            fields = SegmentCategoryListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + SegmentCategoryListSerializer.Meta.read_only_fields + []
