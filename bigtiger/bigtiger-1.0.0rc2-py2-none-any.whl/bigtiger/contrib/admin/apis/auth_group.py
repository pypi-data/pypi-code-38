# -*- coding: utf-8 -*-

from django_restful import RestfulApiView
from django_restful.response import Response

from bigtiger.contrib.admin.models.auth_group import AuthGroupModel
from bigtiger.contrib.admin.serializers.auth_group import AuthGroupSerializer


class AuthGroupList(RestfulApiView):

    def __init__(self):
        self._service = AuthGroupModel()

    def get(self, request, format=None):
        lst = self._service.get_all()
        serializer = AuthGroupSerializer(lst, many=True)
        return Response(serializer.data)


class AuthGroupDetail(RestfulApiView):

    def __init__(self):
        self._service = AuthGroupModel()

    def get_object(self, pk):
        m = self._service.get_one(pk)
        if m is None:
            raise DoesNotExistError(u'记录未找到.')
        return m

    def get(self, request, pk, format=None):
        try:
            m = self.get_object(pk)
            serializer = AuthGroupSerializer(m)
            return Response(serializer.data)
        except DoesNotExistError as ex:
            return ErrorResponse(ex)
