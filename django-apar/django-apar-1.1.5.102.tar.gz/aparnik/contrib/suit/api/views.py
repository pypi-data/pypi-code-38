from django.db.models import Sum, Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import as_serializer_error
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import pagination


class BaseSortAPIView(APIView):
    permission_classes = [AllowAny]
    command_dict = {}

    def __init__(self, *args, **kwargs):
        super(BaseSortAPIView, self).__init__(*args, **kwargs)
        self.command_dict = {

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

        if not self.isAllowKey(ordering.lstrip('-')):
            raise ValidationError({'ordering': [_('This is not valid order parameters for sorting.')]})

        command = self.command_dict[ordering.lstrip('-')]

        if ordering[0] == '-':
            command['key_sort'] = '-' + command['key_sort']

        return queryset.filter(command['queryset_filter']).annotate(**command['annotate_command']).order_by(
            command['key_sort']).distinct()


class BaseListAPIView(ListAPIView):
    # paginator = AdminModelPaginator()
    # permission_classes = [IsAdminUser]

    def filter_queryset(self, queryset, *args, **kwargs):
        queryset = super(BaseListAPIView, self).filter_queryset(queryset)
        sort_api = self.get_sort_api(self.request)
        queryset = sort_api.get_query_sort(queryset)
        return queryset


    def get_sort_api(self, request):
        return BaseSortAPIView(request=request)



class AdminModelPaginator(pagination.PageNumberPagination):

    def get_paginated_response(self, data):
        total_count = 0
        try:
            total_count = self.page.paginator.object_list.aggregate(Sum('sort_count'))['sort_count__sum']
        except:
            total_count = 0

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_count', total_count),
            ('results', data)
        ]))


class ModelAdminSortAPIView(BaseSortAPIView):
    permission_classes = [IsAdminUser]

    def __init__(self, *args, **kwargs):
        super(ModelAdminSortAPIView, self).__init__(*args, **kwargs)
        command_dict = {

        }

        self.command_dict.update(command_dict)


class AdminListAPIView(ListAPIView):
    paginator = AdminModelPaginator()
    permission_classes = [IsAdminUser]

    def filter_queryset(self, queryset, *args, **kwargs):
        queryset = super(AdminListAPIView, self).filter_queryset(queryset)
        sort_api = self.get_sort_api(self.request)
        queryset = sort_api.get_query_sort(queryset)
        return queryset


    def get_sort_api(self, request):
        return ModelAdminSortAPIView(request=self.request)
