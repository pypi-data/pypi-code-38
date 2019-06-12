# -*- coding: utf-8 -*-

from rest_framework import status

from django_restful import RestfulApiView, RestfulApiError, DoesNotExistError, view_http_method
from django_restful.response import ErrorResponse, Response

from bigtiger.contrib.admin.serializers.auth_user_log import AuthUserLogSerializer
from bigtiger.contrib.admin.models.auth_user_log import AuthUserLogModel


class AuthUserLogList(RestfulApiView):

    def __init__(self):
        self._service = AuthUserLogModel()

    def post(self, request, format=None):
        serializer = AuthUserLogSerializer(data=request.data)
        if serializer.is_valid():
            self._service.add(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return ErrorResponse(serializer)
