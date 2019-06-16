# -*- coding: utf-8 -*-


from django.db.models.query import Q
from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import as_serializer_error
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from aparnik.contrib.counters.models import Counter

from ..models import BaseModel
from .serializers import ModelListPolymorphicSerializer, ModelDetailsPolymorphicSerializer


class BaseModelSortAPIView(APIView):
    permission_classes = [AllowAny]
    command_dict = {}

    def __init__(self, *args, **kwargs):
        super(BaseModelSortAPIView, self).__init__(*args, **kwargs)
        self.command_dict = {
            'id': {
                'label': 'شناسه',
                'queryset_filter': Q(),
                'annotate_command': {},
                'key_sort': 'id',
            },
            'review_count': {
                'label': 'تعداد نظرات',
                'queryset_filter': Q(),
                'annotate_command': {},
                'key_sort': 'review_count',
            },
            'qa_count': {
                'label': 'تعداد پرسش و پاسخ',
                'queryset_filter': Q(),
                'annotate_command': {},
                'key_sort': 'qa_count',
            }
        }

    def get(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}
        try:
            content = self.get_sort_content_list()
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))

    def get_sort_content_list(self):
        return [{'key': key, 'label': value['label']} for key, value in list(self.command_dict.items())]

    def isAllowKey(self, key):
        return key in self.command_dict

    def get_query_sort(self, queryset):

        ordering = None

        if 'ordering' in self.request.query_params:
            ordering = self.request.query_params['ordering']
        else:
            return queryset

        if not ordering and self.isAllowKey(ordering.lstrip('-')):
            return queryset

        command = self.command_dict[ordering.lstrip('-')]

        if ordering[0] == '-':
            command['key_sort'] = '-' + command['key_sort']

        return queryset.filter(command['queryset_filter']).annotate(**command['annotate_command']).order_by(
            command['key_sort'])


class BaseModelListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        return BaseModel.objects.active()


class BaseModelDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ModelDetailsPolymorphicSerializer
    queryset = BaseModel.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'model_id'
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        model = get_object_or_404(BaseModel.objects.active(), id=kwargs['model_id'])

        if self.request.user.is_anonymous:
            counter = Counter.objects.create(model_obj=model, action='v')
        else:
            counter = Counter.objects.create(user_obj=self.request.user, model_obj=model, action='v')

        counter.save()
        return RetrieveUpdateDestroyAPIView.get(self, request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        model = get_object_or_404(BaseModel.objects.active(), id=kwargs['model_id'])
        data = request.data.copy()
        # data._mutable = True
        data['resourcetype'] = model.get_real_instance().resourcetype
        serializer = ModelDetailsPolymorphicSerializer(model, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class TagDetailsAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [AllowAny]

    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        return BaseModel.objects.active().filter(tags__id=self.kwargs['model_id'])


# class TagDetailsListAPIView(ListAPIView):
#     serializer_class = ModelListPolymorphicSerializer
#     permission_classes = [AllowAny]
#     #filter_backends = (filters.SearchFilter,)
# search_fields = ('id',)
#
# def get_queryset(self):
#     return BaseModel.objects.all()

class ShareAPIView(APIView):
    status = HTTP_400_BAD_REQUEST
    permission_classes = [AllowAny]

    def get(self, request, model_id, *args, **kwargs):

        model = get_object_or_404(BaseModel.objects.all(), id=model_id)

        try:
            status = HTTP_200_OK
            content = 'The content of share uri link.'
            return Response(content, status=status)

        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)
