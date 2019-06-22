# -*- coding: utf-8 -*-


from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from ..models import Teacher
from .serializers import TeacherListPolymorphicSerializer


# Create your views here.
class TeacherListAPIView(ListAPIView):
    serializer_class = TeacherListPolymorphicSerializer
    queryset = Teacher.objects.active()
    permission_classes = [AllowAny]


class TeacherModelsListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Teacher.objects.active()
        if 'teacher_id' in self.request.parser_context['kwargs']:
            try:
                teacher = Teacher.objects.get(id=self.request.parser_context['kwargs']['teacher_id'])
                return teacher.get_models()
            except Exception as e:
                pass
        return queryset
