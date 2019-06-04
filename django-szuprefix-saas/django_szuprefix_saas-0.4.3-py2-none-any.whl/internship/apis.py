# -*- coding:utf-8 -*-
from .apps import Config

__author__ = 'denishuang'
from . import models
from rest_framework import serializers, viewsets
from django_szuprefix.api.helper import register


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instructor
        fields = ('name', 'department', 'is_active')



class InstructorViewSet(viewsets.ModelViewSet):
    queryset = models.Instructor.objects.all()
    serializer_class = InstructorSerializer



register(Config.label, 'instructor', InstructorViewSet)



class CounsellorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Counsellor
        fields = ('name', 'department', 'is_active')



class CounsellorViewSet(viewsets.ModelViewSet):
    queryset = models.Counsellor.objects.all()
    serializer_class = CounsellorSerializer



register(Config.label, 'counsellor', CounsellorViewSet)



class TraineeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Trainee
        fields = ('name', 'instructor', 'counsellor', 'status', 'comment', 'is_active', 'internship_begin', 'internship_end')

class TraineeFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Trainee



class TraineeViewSet(viewsets.ModelViewSet):
    queryset = models.Trainee.objects.all()
    serializer_class = TraineeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return TraineeFullSerializer
        return super(TraineeViewSet, self).get_serializer_class()

register(Config.label, 'trainee', TraineeViewSet)




class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institution
        fields = ('name', 'internship_type', 'city', 'place')


class InstitutionFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Institution



class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = models.Institution.objects.all()
    serializer_class = InstitutionSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return InstitutionFullSerializer
        return super(InstitutionViewSet, self).get_serializer_class()

register(Config.label, 'institution', InstitutionViewSet)
