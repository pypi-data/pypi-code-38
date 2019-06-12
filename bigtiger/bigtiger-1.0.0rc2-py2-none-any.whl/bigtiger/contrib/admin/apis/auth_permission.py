# -*- coding: utf-8 -*-

from rest_framework import status

from django_restful import RestfulApiView, RestfulApiError, DoesNotExistError, view_http_method
from django_restful.response import ErrorResponse, Response

from bigtiger.contrib.admin.serializers.auth_permission import AuthPermissionSerializer
from bigtiger.contrib.admin.models.auth_permission import AuthPermissionModel


class AuthPermissionList(RestfulApiView):

    def __init__(self):
        self._service = AuthPermissionModel()

    def get(self, request, format=None):
        lst = self._service.get_all()
        serializer = AuthPermissionSerializer(lst, many=True)
        return Response(serializer.data)
