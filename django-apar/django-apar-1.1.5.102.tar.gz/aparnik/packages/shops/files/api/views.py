# -*- coding: utf-8 -*-


from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from ..models import File
from .serializers import FileListPolymorphicSerializer, FileDetailsPolymorphicSerializer
# from courses.models import File, Course
# from libraries.models import Library


class FileListAPIView(ListAPIView):
    serializer_class = FileListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        return File.objects.all()


class FileFileListAPIView(ListAPIView):
    serializer_class = FileListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        # course = get_object_or_404(Course, id=self.request.parser_context['kwargs']['course_id'])
        # return File.objects.filter(course_obj=course)
        # TODO: handle course and etc
        return File.objects.active()

# class BaseFileLibraryListAPIView(ListAPIView):
#     serializer_class = FileListPolymorphicSerializer
#     permission_classes = [AllowAny]
#     # filter_backends = (filters.SearchFilter,)
#
#     def get_queryset(self):
#         queryset = BaseFile.objects.instance_of(Library)
#         return queryset


class FileDownloadRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user
        content = {
            'success': False,
            'msg': '',
            'data': {

            },
        }

        try:
            file = get_object_or_404(File.objects.get_this_user(user=user), id=file_id)

            key = self.request.data.get('key', None)
            if not key:
                content['msg'] += _('key is required')

            if content['msg']:
                raise ValidationError({'__all__': [_(content['msg'])]})

            (content["data"]["key"], content['data']['iv'], content["data"]["url_download"]) = file.get_key_url(
                user=user, key=key)
            content["data"]["url_download"] = self.request.build_absolute_uri(content["data"]["url_download"])
            content["success"] = True
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))
