# -*- coding: utf-8 -*-

from rest_framework import status

from django_restful import RestfulApiView, RestfulApiError, view_http_method
from django_restful.response import ErrorResponse, Response

from bigtiger.contrib.admin.serializers.sys_book import SysBookSerializer
from bigtiger.contrib.admin.models.sys_book import SysBookModel


class SysBookList(RestfulApiView):

    def __init__(self):
        self._service = SysBookModel()

    def get(self, request, format=None):
        lst = self._service.get_all()
        serializer = SysBookSerializer(lst, many=True)
        return Response(serializer.data)

    @view_http_method('get')
    def get_list_class_code(self, request):
        """ 根据class code获取数据。
        """

        query = request.GET.copy()
        class_code = query.get('class_code', None)
        if class_code is None:
            raise RestfulApiError('class_code is null.')

        sort = query.get('sort', 'order_number')
        order = query.get('order', 'asc')

        rows = self._service.get_list_class_code(class_code, sort, order)
        serializer = SysBookSerializer(rows, many=True)
        return Response(serializer.data)
