# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models
from ..saas.mixins import PartySerializerMixin
from ..course import models as course_models
from ..school import models as school_models


class PaperSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Paper
        exclude = ('party', 'content_object', 'content')
        read_only_fields = ('user', 'questions_count')


class PaperFullSerializer(PaperSerializer):
    class Meta(PaperSerializer.Meta):
        exclude = ('party',)


class PaperInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Paper
        fields = ('title', 'id', 'questions_count', 'is_break_through')


class ChapterPaperSerializer(serializers.ModelSerializer):
    exam_papers = PaperInfoSerializer(many=True, read_only=True)

    class Meta:
        model = course_models.Chapter
        fields = ('id', 'name', 'exam_papers')


class CoursePaperSerializer(PartySerializerMixin, serializers.ModelSerializer):
    chapters = ChapterPaperSerializer(many=True, read_only=True)
    exam_papers = PaperInfoSerializer(many=True, read_only=True)

    class Meta:
        model = course_models.Course
        fields = ('id', 'name', 'chapters', 'exam_papers')


class AnswerSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        exclude = ('party',)
        read_only_fields = ('user', 'paper')

class AnswerListSerializer(AnswerSerializer):
    class Meta(AnswerSerializer.Meta):
        exclude = ('party', 'detail')


class StatSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stat
        exclude = ('party',)
        # fields = ('detail',)


class PerformanceSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    paper_name = serializers.CharField(source="paper.__str__", label='试卷', read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", label='学生', read_only=True)

    class Meta:
        model = models.Performance
        exclude = ()
        # fields = ('paper_id', 'score', 'detail')
        extra_kwargs = {'paper': {'read_only': True}, 'party': {'read_only': True}, 'user': {'read_only': True}}
