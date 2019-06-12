# -*- coding: utf-8 -*-

from rest_framework import status

from django_restful import RestfulApiView, RestfulApiError, DoesNotExistError, view_http_method
from django_restful.response import ErrorResponse, Response

from bigtiger.contrib.admin.serializers.auth_session import AuthSessionSerializer, AuthSessionPagerSerializer
from bigtiger.contrib.admin.models.auth_session import AuthSessionModel


class AuthSessionList(RestfulApiView):

    def __init__(self):
        self._service = AuthSessionModel()

    def get(self, request, format=None):
        sessions = self._service.get_all()
        serializer = AuthSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AuthSessionSerializer(data=request.data)
        if serializer.is_valid():
            self._service.add(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return ErrorResponse(serializer)

    @view_http_method('get')
    def page_query(self, request):
        query = request.GET.copy()
        limit = query.get('limit', 20)
        offset = query.get('offset', 0)
        sort = query.get('sort', None)
        order = query.get('order', None)

        rows, count = self._service.get_page_query(limit, offset, sort, order)
        serializer = AuthSessionPagerSerializer({'count': count, 'data': rows})
        return Response(serializer.data)

    @view_http_method(['put', 'post'])
    def exists_modify(self, request):
        serializer = AuthSessionSerializer(data=request.data)
        if serializer.is_valid():
            self._service.exist_modify(serializer.data)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return ErrorResponse(serializer)

    @view_http_method(['post', 'delete'])
    def tran_delete(self, request):
        pks = request.POST.get('pks')
        pks = pks.split('|')
        self._service.tran_delete(pks)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @view_http_method(['post', 'delete'])
    def clear(self, request):
        self._service.tran_clear()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @view_http_method(['post', 'delete'])
    def clear_expired(self, request):
        self._service.tran_clear_expired()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthSessionDetail(RestfulApiView):

    def __init__(self):
        self._service = AuthSessionModel()

    def get_object(self, pk):
        m = self._service.get_one(pk)
        if m is None:
            raise DoesNotExistError(u'记录未找到.')
        return m

    def get(self, request, pk, format=None):
        try:
            m = self.get_object(pk)
            serializer = AuthSessionSerializer(m)
            return Response(serializer.data)
        except DoesNotExistError as ex:
            return ErrorResponse(ex)

    def put(self, request, pk, format=None):
        serializer = AuthSessionSerializer(data=request.data)
        if serializer.is_valid():
            self._service.modify(pk, serializer.data)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return ErrorResponse(serializer)

    def delete(self, request, pk, format=None):
        self._service.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
