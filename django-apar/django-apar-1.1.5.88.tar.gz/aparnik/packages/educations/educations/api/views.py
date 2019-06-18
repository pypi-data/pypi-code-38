# -*- coding: utf-8 -*-


from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from .serializers import BaseEducationListPolymorphicSerializer, EducationDetailsSerializers
from ..models import Education, Institute, FieldSubject, Degree


# Create your views here.
class BaseEducationListAPIView(ListAPIView):
    serializer_class = BaseEducationListPolymorphicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Education.objects.active()
        return queryset


class InstituteListAPIView(ListAPIView):
    serializer_class = BaseEducationListPolymorphicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Institute.objects.active()
        return queryset


class FieldSubjectListAPIView(ListAPIView):
    serializer_class = BaseEducationListPolymorphicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = FieldSubject.objects.active()
        return queryset


class DegreeListAPIView(ListAPIView):
    serializer_class = BaseEducationListPolymorphicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Degree.objects.active()
        return queryset


class EducationCreateAPIView(CreateAPIView):
    serializer_class = EducationDetailsSerializers  # EducationCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer, **kwargs):
        user = self.request.user
        dict = {
            'user_obj': user,
        }

        serializer.save(**dict)


class EducationUpdateAPIView(UpdateAPIView):
    serializer_class = EducationDetailsSerializers
    queryset = Education.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'education_id'
    lookup_field = 'basemodel_ptr_id'

    def perform_update(self, serializer, **kwargs):
        user = self.request.user
        dict = {
            'user_obj': user,
        }

        serializer.save(**dict)
