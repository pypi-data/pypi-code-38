# -*- coding:utf-8 -*-
from django_szuprefix.utils.statutils import do_rest_stat_action
from rest_framework.decorators import list_route, detail_route
from django_szuprefix_saas.saas.mixins import PartyMixin
from django_szuprefix_saas.school.permissions import IsStudent, IsTeacher
from .apps import Config

__author__ = 'denishuang'
from . import models, serializers, stats
from rest_framework import viewsets, response
from django_szuprefix.api.helper import register


class CourseViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    search_fields = ('name', 'code')
    filter_fields = ('is_active', 'category', 'code')
    ordering_fields = ('is_active', 'title', 'create_time')

    def get_queryset(self):
        qset = super(CourseViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('course.view_all_course'):
            pass
        elif hasattr(user, 'as_school_student'):
            student = user.as_school_student
            # from django.db.models import Q
            # qset = qset.filter(Q(school_students=student) | Q(school_classes=student.clazz)).filter(is_active=True).distinct()
            qset = student.all_courses
        elif hasattr(user, 'as_school_teacher'):
            qset = qset.filter(clazz_course_relations__teacher_id=user.as_school_teacher.id).filter(is_active=True).distinct()
        else:
            qset = qset.none()
        return qset

    # @list_route(['get'], permission_classes=[IsStudent])
    # def for_student(self, request):
    #     # major = self.student.majors.first()
    #     courses = self.student.all_courses
    #     # courses = self.party.course_courses.filter(is_active=True, majors__in=self.student.majors.all())
    #     page = self.paginate_queryset(courses)
    #     serializer = self.get_serializer(page, many=True)
    #     return self.get_paginated_response(serializer.data)
    #
    # @list_route(['get'], permission_classes=[IsTeacher])
    # def for_teacher(self, request):
    #     return self.get_paginated_response(self.get_serializer(self.paginate_queryset(
    #         self.teacher.courses.distinct()
    #     ), many=True
    #     ).data)

    @list_route(['get'])
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_course)


register(Config.label, 'course', CourseViewSet)


class CategoryViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    search_fields = ('name', 'code')
    filter_fields = ('code', 'name')


register(Config.label, 'category', CategoryViewSet)


class ChapterViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer
    search_fields = ('name', 'code')
    filter_fields = ('course',)


register(Config.label, 'chapter', ChapterViewSet)
