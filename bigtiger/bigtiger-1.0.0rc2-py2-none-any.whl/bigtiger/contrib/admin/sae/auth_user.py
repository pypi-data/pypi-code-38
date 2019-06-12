# -*- coding: utf-8 -*-

from rest_framework import status

from django_restful import RestfulApiView, RestfulApiError, DoesNotExistError, view_http_method
from django_restful.response import ErrorResponse, Response

from bigtiger.contrib.admin.serializers.auth_user import AuthUserSerializer
from bigtiger.contrib.admin.serializers.auth_permission import AuthPermissionSerializer
from bigtiger.contrib.admin.models.auth_user import AuthUserModel
from bigtiger.contrib.admin.models.auth_permission import AuthPermissionModel


class AuthUserList(RestfulApiView):

    def __init__(self):
        self._service = AuthUserModel()

    def get(self, request, format=None):
        users = self._service.get_all()
        serializer = AuthUserSerializer(users, many=True)
        return Response(serializer.data)

    @view_http_method('POST')
    def authenticate(self, request):
        login_name = request.POST.get('login_name', None)
        login_pwd = request.POST.get('login_pwd', None)
        if login_name and login_pwd:
            m = self._service.get_one_login_name(login_name)
            if m is None or m['login_password'] != login_pwd:
                return ErrorResponse(u'用户名或密码错误。')

            serializer = AuthUserSerializer(m)
            return Response(serializer.data)
        return ErrorResponse(u'login_name和login_pwd参数不能为空。')


class AuthUserDetail(RestfulApiView):

    def __init__(self):
        self._service = AuthUserModel()

    def get_object(self, pk):
        user = self._service.get_one(pk)
        if user is None:
            raise DoesNotExistError(u'未找到该用户.')
        return user

    def get(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
            serializer = AuthUserSerializer(user)
            return Response(serializer.data)
        except DoesNotExistError as ex:
            return ErrorResponse(ex)

    @view_http_method('GET')
    def get_user_permissions(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
            m = AuthPermissionModel()

            permissions = []
            if user.get('is_superuser', 0) == 1:
                permissions = m.get_list_system()
            else:
                role_str = user.get('roles', '')
                roles = role_str.split(',')
                permissions = m.get_list_groups(roles)

            serializer = AuthPermissionSerializer(permissions, many=True)
            return Response(serializer.data)
        except DoesNotExistError as ex:
            return ErrorResponse(ex)

    @view_http_method(['POST', 'PUT'])
    def modify_pwd(self, request, pk, format=None):
        try:
            old_pwd = request.POST.get('old_pwd', None)
            new_pwd = request.POST.get('new_pwd', None)

            if old_pwd is None:
                return ErrorResponse(u'旧密码未能为空。')
            if new_pwd is None:
                return ErrorResponse(u'新密码未能为空。')

            user = self.get_object(pk)
            if user['login_password'] != old_pwd:
                return ErrorResponse(u'旧密码错误。')

            self._service.modify_pwd(pk, new_pwd)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DoesNotExistError as ex:
            return ErrorResponse(ex)
