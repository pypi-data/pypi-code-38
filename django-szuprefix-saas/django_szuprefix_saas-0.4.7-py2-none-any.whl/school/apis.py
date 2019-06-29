# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import django_filters
from django_szuprefix.utils.statutils import do_rest_stat_action

from .apps import Config

from . import models, mixins, serializers, importers, helper, permissions, stats
from rest_framework import viewsets, decorators, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django_szuprefix.api.helper import register

__author__ = 'denishuang'


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


register(Config.label, 'school', SchoolViewSet)


class TeacherViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    # permission_classes = [DjangoModelPermissionsWithView]
    filter_fields = ('name',)
    search_fields = ('name', 'code')

    @decorators.list_route(['get'])
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_teacher)


register(Config.label, 'teacher', TeacherViewSet)


class GradeViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Grade.objects.all()
    serializer_class = serializers.GradeSerializer


register(Config.label, 'grade', GradeViewSet)


class SessionViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
    search_fields = ('name', 'number')
    filter_fields = {'id': ['in', 'exact']}

    # def get_queryset(self):
    #     return super(SessionViewSet, self).get_queryset().filter(
    #         school=self.request.user.as_saas_worker.party.as_school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.as_saas_worker.party.as_school)


register(Config.label, 'session', SessionViewSet)


class ClazzViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Clazz.objects.all()
    serializer_class = serializers.ClazzSerializer
    search_fields = ('name', 'code')
    filter_fields = ('name', 'code', 'entrance_session', 'grade')

    def get_queryset(self):
        qset = super(ClazzViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('school.view_all_clazz'):
            pass
        elif hasattr(user, 'as_school_teacher'):
            qset = qset.filter(clazz_course_relations__teacher=user.as_school_teacher).distinct()
        elif hasattr(user, 'as_school_student'):
            qset = qset.filter(id=user.as_school_student.clazz_id).distinct()
        else:
            qset = qset.none()
        return qset

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ClazzSmallSerializer
        return super(ClazzViewSet, self).get_serializer_class()

    # @decorators.list_route(methods=['get'], permission_classes=[permissions.IsTeacher])
    # def for_teacher(self, request):
    #     qset = self.get_queryset().filter(clazz_course_relations__teacher=self.teacher)
    #     return self.get_paginated_response(
    #         serializers.ClazzSmallSerializer(self.paginate_queryset(qset), many=True).data)

    @decorators.list_route(['get'])
    def similar(self, request):
        q = request.query_params.get('q')
        import Levenshtein
        from django.db.models import F
        from django_szuprefix.utils.modelutils import CharCorrelation
        qset = self.filter_queryset(self.get_queryset()).values('name', a=CharCorrelation([F('name'), q])).filter(
            a__gt=0).order_by('-a').values_list('name', 'a')[:10]
        aa = [(Levenshtein.ratio(n, q), c, n) for n, c in qset]
        aa.sort(reverse=True)
        ss = [c for a, b, c in aa if a > 0.5]
        return Response({'similar':ss})

    @decorators.list_route(['get'])
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_clazz)


register(Config.label, 'clazz', ClazzViewSet)


class MajorViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Major.objects.all()
    serializer_class = serializers.MajorSerializer
    search_fields = ('name', 'code')
    filter_fields = {'code': ['exact'], 'name': ['exact', 'in']}


register(Config.label, 'major', MajorViewSet)


class CollegeViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.College.objects.all()
    serializer_class = serializers.CollegeSerializer
    search_fields = ('name', 'code')
    filter_fields = ('code', 'name',)


register(Config.label, 'college', CollegeViewSet)


class ClazzCourseViewSet(mixins.PartyMixin, viewsets.ModelViewSet):
    queryset = models.ClazzCourse.objects.all()
    serializer_class = serializers.ClazzCourseSerializer
    search_fields = ('clazz__name', 'course__name')
    filter_fields = {'id': ['in', 'exact'], 'clazz': ['exact'], 'course': ['exact'], 'teacher': ['exact']}

    def get_queryset(self):
        qset = super(ClazzCourseViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('school.view_all_clazzcourse'):
            pass
        elif hasattr(user, 'as_school_teacher'):
            qset = qset.filter(teacher=user.as_school_teacher)
        else:
            qset = qset.none()
        return qset

    # @decorators.list_route(methods=['get'], permission_classes=[permissions.IsTeacher])
    # def for_teacher(self, request):
    #     qset = self.filter_queryset(self.get_queryset()).filter(teacher=self.teacher)
    #     return self.get_paginated_response(self.get_serializer(self.paginate_queryset(qset), many=True).data)


register(Config.label, 'clazzcourse', ClazzCourseViewSet)


class StudentViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    # permission_classes = [DjangoModelPermissionsWithView]
    search_fields = ('name', 'number', 'code')
    filter_fields = ('grade', 'clazz', 'number', 'is_active', 'is_bind')
    ordering_fields = '__all__'

    # permission_classes = mixins.SchoolMixin.permission_classes+[DjangoModelPermissionsWithView]

    def get_queryset(self):
        qset = super(StudentViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('school.view_all_student'):
            pass
        elif hasattr(user, 'as_school_teacher'):
            teacher = user.as_school_teacher
            qset = teacher.students
        else:
            qset = qset.none()
        return qset

    # def get_serializer_class(self):
    #     user = self.request.user
    #     if user.has_perm('school.view_student_sensitivity'):
    #         return serializers.StudentSerializer
    #     return super(StudentViewSet, self).get_serializer_class()

    def get_permissions(self):
        if self.action == 'binding':
            return [IsAuthenticated()]
        return super(StudentViewSet, self).get_permissions()

    @decorators.list_route(['post'])
    def pre_import(self, request):
        importer = importers.StudentImporter(self.school)
        data = importer.clean(importer.get_excel_data(request.data['file']))
        return Response(data)

    @decorators.list_route(['post'])
    def post_import(self, request):
        importer = importers.StudentImporter(self.school)
        student, created = importer.import_one(request.data)
        return Response(self.get_serializer(instance=student).data,
                        status=created and status.HTTP_201_CREATED or status.HTTP_200_OK)

    @decorators.list_route(['POST'])
    def batch_active(self, request):
        a = request.data.get('is_active', 'true')
        is_active = not (a is False or a == 'false')
        ids = request.data.get('ids', [])
        rows = self.get_queryset().filter(id__in=ids).update(is_active=is_active)
        return Response({'rows': rows})

    @decorators.list_route(['post'], permission_classes=[IsAuthenticated])
    def binding(self, request):
        serializer = serializers.StudentBindingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            schools = serializer.save()
            data = serializer.data
            data['schools'] = schools
            return Response(data)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.list_route(['POST'])
    def batch_unbind(self, request):
        ids = request.data.get('ids', [])
        for student in self.get_queryset().filter(id__in=ids):
            helper.unbind(student)
        return Response({'rows': len(ids)})

    @decorators.detail_route(['post'])
    def unbind(self, request):
        helper.unbind(self.get_object())
        return Response({'info': 'success'})

    @decorators.list_route(['get'])
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_student)


register(Config.label, 'student', StudentViewSet)
