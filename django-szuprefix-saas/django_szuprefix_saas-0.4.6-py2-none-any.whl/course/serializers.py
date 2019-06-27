# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from . import models
from ..saas.mixins import PartySerializerMixin


class CourseSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.__str__", read_only=True)
    chapters = serializers.ManyRelatedField
    exam_papers_name = serializers.CharField(label="试卷", read_only=True)
    class Meta:
        model = models.Course
        exclude = ('party',)
        validators = [
            UniqueTogetherValidator(
                queryset=models.Course.objects.all(),
                fields=('party', 'code')
            )
        ]

class CategorySerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = ('party',)


class ChapterSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.__str__", read_only=True)
    exam_papers_name = serializers.CharField(label="试卷", read_only=True)
    class Meta:
        model = models.Chapter
        exclude = ('party',)
