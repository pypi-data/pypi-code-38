# -*- coding: utf-8 -*-


from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from ..models import Progresses
# from aparnik.packages.educations.progresses.api.serializers import BaseProgressListPolymorphicSerializer


# class ProgressListAPIView(ListAPIView):
#     serializer_class = BaseProgressListPolymorphicSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         user_obj = self.request.user
#         queryset = Progresses.objects.active(user_obj)
#         return queryset
#
#
class ProgressSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        content = {
            'is_update': False
        }
        from aparnik.packages.shops.files.models import File
        user = self.request.user
        status = self.request.data.get('status', None)

        file_obj = get_object_or_404(File.objects.all(), id=file_id)

        try:
            obj = get_object_or_404(Progresses.objects.filter(file_obj=file_obj), user_obj=user)
            obj.status = status
            obj.update_needed = True
            obj.save()
            content['is_update'] = True
            status = HTTP_200_OK

        except Exception as e:
            try:

                obj = Progresses.objects.create(user_obj=user, file_obj=file_obj,
                                                status=status,
                                                is_published=True,
                                                update_needed=True
                                                )
                obj.save()
                content['is_update'] = True
                status = HTTP_200_OK
            except Exception as e:
                raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)

#
#
# class ProgressUpdateAPIView(UpdateAPIView):
#     serializer_class = ProgressDetailsSerilizer
#     queryset = Progresses.objects.all()
#     permission_classes = [IsAuthenticated]
#     lookup_url_kwarg = 'progress_id'
#
#     def perform_update(self, serializer, **kwargs):
#         user = self.request.user
#         dict = {
#             'user_obj': user,
#         }
#
#         serializer.save(**dict)
