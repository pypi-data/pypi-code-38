# -*- coding: utf-8 -*-


from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from ..models import Page


# Category List Serializer
class PageListSerializer(BaseModelListSerializer):

    class Meta:
        model = Page
        fields = BaseModelListSerializer.Meta.fields + [
            'title',
            'english_title',
        ]


# Category Details Serializer
class PageDetailsSerializer(PageListSerializer, BaseModelDetailSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = PageListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'content',
        ]

    def get_content(self, obj):
        from aparnik.contrib.segments.models import PageSort
        from aparnik.contrib.segments.api.serializers import PageSortListSerializer
        return PageSortListSerializer(PageSort.objects.filter(page_obj=obj), many=True, read_only=True,
                                                   context=self.context).data


# Category List Polymorphic
class PageListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            Page: PageListSerializer,
        }
        super(PageListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Category Details Polymorphic
class PageDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            Page: PageDetailsSerializer,
        }
        super(PageDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
