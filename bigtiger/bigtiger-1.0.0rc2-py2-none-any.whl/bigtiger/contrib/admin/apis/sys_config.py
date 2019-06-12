# -*- coding: utf-8 -*-

from django_restful import RestfulApiView
from django_restful.response import Response

from bigtiger.contrib.admin.serializers.sys_config import SysConfigSerializer
from bigtiger.contrib.admin.models.sys_config import SysConfigModel


class SysConfigList(RestfulApiView):

    def __init__(self):
        self._service = SysConfigModel()

    def get(self, request, format=None):
        lst = self._service.get_all()
        serializer = SysConfigSerializer(lst, many=True)
        return Response(serializer.data)
